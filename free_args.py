#!/usr/bin/env python

''' Copyright (C) 2014 TTK Ciar
    This file may be used, modified, and distributed without restriction.
'''

''' free_args is an implementation of a "free-form" style commandline argument
    parser.  Rather than predeclaring what all of your options will be, simply
    use the "opt" method wherever you need an option to be used, and everything
    will jfw.  Yay for dynamic languages!

    Run this module as a script to exercise its unit tests.

    IMPORTANT NOTE: Option names with '-' in them will have all '-' changed
    into '_'!  This is a holdover from the perl version of this code, and I'm
    not sure if carrying it over to python makes 100% sense.  Let me know
    what you think.

    Some downsides to this approach:
        * Will not throw an error when users provide an invalid option.
        * Does not support the "-x 4" convention, only "-x" or "--x=4".
        * It's easy to accidentally create many options that do the same thing
          in different parts of the code with slightly different names.
        * In the absence of a default value in an opt() call, opt() might not
          always return a value of the expected type.

    SYNOPSIS

        # standalone approach:

        from free_args import FreeArgs

        farg = FreeArgs()
        farg.parse_args()

        if farg.opt('some_arg'): print "yay!"
        print "n = %d" % farg.opt('n', 1)

        for filename in self.doc_list:
            process_file(filename)

        # subclass approach:

        from free_args import FreeArgs

        class MyClass(FreeArgs):

            def __init__(self):
                FreeArgs.__init__(self)

            def main(self):
                self.parse_args()
                print "n = %d" % farg.opt('n', 1)
                for doc in self.doc_list:
                    self.process_document(doc)

    The latest version of this module can be found at: https://github.com/ttkciar/free_args

    If github should cease to exist, check: https://ciar.org/ttk/codecloset/ and there should at least be a notation as to where to look.
'''

import re
import sys
import json
import unittest


class FreeArgs(object):

    ''' Either make your main class inherit from FreeArgs and call
        self.parse_args() and self.opt('foo', 0), or instantiate it as a
        standalone (like: farg = FreeArgs()) and call farg.parse_args()
        and farg.opt('foo', 0).  It will work either way.
    '''

    def __init__(self):
        self.ctl_dict = dict()  # --foo=42 --> ctl_dict['foo'] = 42
        self.doc_list = list()  # Non-option arguments get put here.

    def opt(self, label, default_value=None, local_dict={}):
        ''' Given the name of an option, will try to find it in a few places,
            and return default_value if that option is not found anywhere.

            local_dict would be for any options local to a method or other
            context which should take priority over any other options.  If
            this means nothing to you, don't worry about it and just don't
            use it.

            If self has a config_dict, it will be checked *after* ctl_dict,
            which means commandline options override options read from your
            configuration file.  If your application has a config dict but
            you are using FreeArgs as a standalone class, you can simply
            setattr(farg, 'config_dict', your_apps_config_dict) to make it
            all jfw.

            Configuration and commandline options should be stored in
            separate dicts so that if a configuration is re-read from disk,
            commandline options will not be overwritten.
        '''
        v = None
        if label in local_dict:
            v = local_dict[label]
        elif label in self.ctl_dict:
            v = self.ctl_dict[label]
        elif 'config_dict' in self.__dict__ and label in self.config_dict:
            v = self.config_dict[label]
        else:
            return default_value

        # If caller provided a default_value, we can try to coerce v to the
        # correct type (string, float, or int).  Otherwise it will probably
        # be returned as a string (barring use of --label=json: syntax).

        if default_value == None: return v
        if type(v).__name__ == 'dict': return v  # --label=json:{..} syntax
        if type(v).__name__ == 'list': return v  # --label=json:[..] syntax

        if type(default_value).__name__ == 'int':
            if type(v).__name__ not in ['str', 'unicode']: return int(v)
            hits = re.search('(-?\d+)', v)
            if hits == None: return 0
            return int(hits.group(1))

        if type(default_value).__name__ == 'float':
            if type(v).__name__ not in ['str', 'unicode']: return float(v)
            hits = re.search('(-?\d[\d\.e\+]*)', v)
            if hits == None: return 0.0
            try: return float(hits.group(1))
            except: Pass
            return 0.0

        if type(default_value).__name__ == 'str':
            try: return str(v)
            except: Pass
            return ''

        # fuckit, we tried our best.
        return v

    def parse_args(self, arg_list=sys.argv[1:]):
        ''' Argument  --> Result:

            -xy       --> ctl_dict['x'] = -1; ctl_dict['y'] = -1;

            --foo     --> ctl_dict['foo'] = -1

            --foo=bar --> ctl_dict['foo'] = 'bar'

            IMPORTANT NOTE!!  '-' in option names will be turned into '_'!!

            --some-arg=4 --> ctl_dict['some_arg'] = '4'

            --blarg=json:'{"ichi": "ni", "san": 42}'
                      --> ctl_dict['blarg'] = {"ichi": "ni", "san": 42}

            --stuff=json:'[3, 5, 7, 9]'
                      --> ctl_dict['blarg'] = [3, 5, 7, 9]

            something --> doc_list.append('something')
        '''
        self.ctl_dict = dict()
        self.doc_list = list()

        for arg in arg_list:

            hits = re.match('-([^-].*)', arg)
            if hits != None:
                for c in hits.group(1):
                    self.ctl_dict[c] = -1
                continue

            hits = re.match('--+([^=]+)=json:(.+)', arg)
            if hits != None:
                label = self._transform_label(hits.group(1))
                self.ctl_dict[label] = json.loads(hits.group(2))
                continue

            hits = re.match('--([^=]+)=(.*)', arg)
            if hits != None:
                label = self._transform_label(hits.group(1))
                self.ctl_dict[label] = hits.group(2)
                continue

            hits = re.match('--(.*)', arg)
            if hits != None:
                label = self._transform_label(hits.group(1))
                self.ctl_dict[label] = -1
                continue

            self.doc_list.append(arg)

        return (len(self.ctl_dict), len(self.doc_list))

    def _transform_label(self, raw_label):
        # uncomment the first return to disable this transformation:
        # return raw_label
        return '_'.join(raw_label.split('-'))


class Test_FreeArgs(unittest.TestCase):

    def test_00_init(self):
        fa = FreeArgs()
        self.assertEquals(type(fa.ctl_dict).__name__,'dict')
        self.assertEquals(type(fa.doc_list).__name__, 'list')
        return fa

    def test_01_parse_args(self):
        fa = FreeArgs()
        test_arg_list = [
            '-xyz',
            '--abc-def',
            '--qwe-rty=foo',
            'faz',
            '--qwe-rty=bar',
            'baz',
            '--complex=json:["ichi", "ni", "san", "shi"]',
            '--finally=42'
        ]
        (n_opt, n_doc) = fa.parse_args(test_arg_list)
        self.assertEquals(n_opt, 7)
        self.assertEquals(n_doc, 2)
        return fa

    def test_02_opt(self):
        fa = self.test_01_parse_args()
        opt_dict = {"x": 5, "gronk": 69}
        self.assertEquals(fa.opt('x'), -1)
        self.assertEquals(fa.opt('x', None, opt_dict), 5)
        self.assertEquals(fa.opt('y'), -1)
        self.assertEquals(fa.opt('z'), -1)
        self.assertEquals(fa.opt('xyz'), None)
        self.assertEquals(fa.opt('xyz', 1), 1)
        self.assertEquals(fa.opt('gronk'), None)
        self.assertEquals(fa.opt('gronk', 'foo'), 'foo')
        self.assertEquals(fa.opt('gronk', 'foo', opt_dict), '69')
        self.assertEquals(fa.opt('gronk', 12345, opt_dict), 69)
        self.assertEquals(fa.opt('abc-def'), None)
        self.assertEquals(fa.opt('abc_def'), -1)
        self.assertEquals(fa.opt('abc_def', 42), -1)
        self.assertEquals(fa.opt('abc_def', 42, opt_dict), -1)
        self.assertEquals(fa.opt('qwe_rty'), "bar")
        self.assertEquals(type(fa.opt('complex')).__name__, "list")
        self.assertEquals(fa.opt('complex')[3], "shi")
        self.assertEquals(fa.opt('finally'), "42")
        self.assertEquals(fa.opt('finally', 1), 42)


if __name__ == '__main__': unittest.main()
