#!/usr/bin/env python
# -*- coding: utf-8 -*-
# :noTabs=true:

# (c) Copyright Rosetta Commons Member Institutions.
# (c) This file is part of the Rosetta software suite and is made available under license.
# (c) The Rosetta software is developed by the contributing members of the Rosetta Commons.
# (c) For more information, see http://www.rosettacommons.org. Questions about this can be
# (c) addressed to University of Washington CoMotion, email: license@uw.edu.

## @file   sphinx-doc-generator.py
## @brief  Script to generate Sphinx documentation files out of Binder output
## @author Sergey Lyskov

from __future__ import print_function

import os, sys, argparse

_javascript_name_ = 'summary.js'

_template_ = '''
{name}
{name_underline}

.. toctree::
    :maxdepth: 1

    {sub_modules}

.. container:: cfv-summary

    .. raw:: html

        <script type="text/javascript" src='{javascript_path}/{_javascript_name_}'></script>


.. automodule:: {module}
    :members:
    :show-inheritance:
    :private-members:
    :special-members:
    :inherited-members:

..    :undoc-members:
..    :special-members:

'''

_javascript_template_ = '''$(function (){
function create_list(selector) {

    ul = $('<ul>');
    selected = $(selector);

    if (selected.length === 0){
        return;
    }

    selected.clone().each(function (i,e){

        p = $(e).children('.descclassname');
        n = $(e).children('.descname');
        l = $(e).children('.headerlink');

        a = $('<a>');
        a.attr('href',l.attr('href')).attr('title', 'definition');

        a.append(p).append(n);

        entry = $('<li>').append(a);
        ul.append(entry);
    });
    return ul;
}

c = $('<div style="float:center; min-width: 450px;">');

ul0 = c.clone().append($('.submodule-index'))

summary = $('.cfv-summary');
summary.empty();
summary.append(ul0);

x = [];
x.push(['Classes:',  'dl.class > dt']);
x.push(['Functions:','dl.function > dt']);
x.push(['Variables:','dl.data > dt']);

x.forEach(function (e){
    l = create_list(e[1]);
    if (l) {
        ul = c.clone()
            .append('<p class="rubric">'+e[0]+'</p>')
            .append(l);
    }
    summary.append(ul);
});
});
'''


def generate_rst_sphinx_files(modules, output_dir, javascript_path):
    for module in modules:
        name = module.split('.')[-1]
        sub_modules = (m for m in modules if '.'.join( m.split('.')[:-1] ) == module)
        sub_modules = '\n    '.join(sub_modules)

        file_name = output_dir + '/' + module + '.rst'

        with open(file_name, 'w') as f: f.write( _template_.format(_javascript_name_=_javascript_name_, name_underline='-'*len(name), **vars()) )



def collect_python_modules(root_dir, name=None):
    if name is None: name = os.path.basename(root_dir)

    items = os.listdir(root_dir)
    if '__init__.py' in items:
        items.remove('__init__.py')

        r = [name]

        for f in items:
            if os.path.isfile(root_dir+'/'+f) and f.endswith('.py'): r.append( name + '.' + f[:-len('.py')])
            if os.path.isdir(root_dir+'/'+f): r.extend( [ name + '.' + i for i in collect_python_modules(root_dir + '/' + f)] )

        return r

    else:
        return []


def main(args):
    ''' Binding demo build/test script '''

    parser = argparse.ArgumentParser()

    parser.add_argument('--root', default=None, help='Name of the root module that was used when invocing Binder. Default: extract name from "module_file" positional command line argument.')
    parser.add_argument('-o', '--output', default='.', help='Path to output directoty. Default is to use current dir')
    parser.add_argument('--javascript-path',  help='Path to directoty where custom javascript file should be writen. Point this to source/_static/ of your Sphinx project.')
    parser.add_argument('--javascript-web-path', default='_static', help='Path to directoty where custom javascript file should writen. Point this to where build/_static/ will be located relative to generated files.')

    parser.add_argument("module_file", help='Path to <root>.module file generated by Binder. If path to dir is supplied instead then treat this dir as root dir for Python modules and generate module list by recursivly walking it.')

    Options = parser.parse_args()

    if Options.root is None: Options.root = os.path.basename(Options.module_file).split('.')[0]

    output_dir = os.path.abspath(Options.output)
    if not os.path.isdir(output_dir): os.makedirs(output_dir)

    if os.path.isdir(Options.module_file):
        print( '{Options.module_file} is a directory... treating it as root to Python module and collecting sub-modules info...'.format(**vars()) )
        modules = collect_python_modules(Options.module_file, name=Options.root)
    else:
        with open(Options.module_file) as f: modules = [Options.root] + [Options.root + '.' + m for m in f.read().split()]  # if m.count('.') < 1

    modules.sort()
    generate_rst_sphinx_files(modules, Options.output, Options.javascript_web_path)


    if Options.javascript_path:
        with open(Options.javascript_path + '/' + _javascript_name_, 'w') as f: f.write(_javascript_template_)


if __name__ == "__main__":
    main(sys.argv)
