free_args
=========

free_args is a more convenient Getopt/argparse alternative commandline options parser for Python.

Rather than predeclaring what all of your options will be, simply use the "opt" method wherever you need an option to be used, and everything will jfw.  Yay for dynamic languages!

The free_args.py has no dependencies outside of the python 2.6/2.7 core libraries.  Run the free_args.py module as a script to exercise its unit tests.

free_args is extremely convenient, but there are some downsides to its approach:

* Will not throw an error when users provide an invalid option.

* Does not support the "-x 4" or "-x4" conventions, only "-x" or "--x=4".

* It's easy to accidentally create many options that do the same thing in different parts of the code with slightly different names.

* In the absence of a default value in an opt() call, opt() might not always return a value of the expected type.  It is best to always provide a default value when using opt().

IMPORTANT NOTE: Option names with '-' in them will have all '-' changed into '_'!  Thus use opt('foo_bar') to access the value of commandline argument "--foo-bar=4".  This is a holdover from the perl version of this code, and I'm not sure if carrying it over to python makes 100% sense.  Let me know what you think.

SYNOPSIS
========

    # standalone approach:

    from free_args import FreeArgs

    args = FreeArgs()
    args.parse_args()

    if args.opt('some_arg'): print "yay!"
    print "n = %d" % args.opt('n', 1)

    for filename in self.doc_list:
        process_file(filename)

    # subclass approach:

    from free_args import FreeArgs

    class MyClass(FreeArgs):

        def __init__(self):
            FreeArgs.__init__(self)

        def main(self):
            self.parse_args()
            print "n = %d" % args.opt('n', 1)
            for doc in self.doc_list:
                self.process_document(doc)
