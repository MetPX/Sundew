"""
#############################################################################################
# Name: PXRetransCompleter
#
# Author: Daniel Lemay
#
# Date: 2007-11-30
#
# Description: Used to complete commands when using pxRetrans in command line mode
#
#############################################################################################
"""

import readline

rules = {'START': ['cmd', 'oneDash', 'twoDashs'], 'cmd':['NOTHING'], 'oneDash':['oneDash', 'twoDashs', 'NOTHING'], 'twoDashs':['oneDash', 'twoDashs', 'NOTHING']}

class PXRetransCompleter(object):
    def __init__(self):
        self.cmds = ['h', 'lo', 'l', 'salut', 'rtx', 'reset', 'f', 'fc', 'fs', 'cf', 'cfc', 'cfs', 'q']
        self.oneLetterOpts = ['-s', '-o', '-c', '-r', '-g', '-p']
        self.opts = ['--span', '--offset', '--startDate', '--endDate', '--sources', '--clients', '--regex', '--group', '--prio', '--scp']
        self.nothing = []

    def complete(self, text, state):
        tokens = readline.get_line_buffer().split()
        if len(tokens) == 0:
            results = [cmd for cmd in self.cmds if cmd.startswith(text)] + [None]
        
        if len(tokens) == 1 and len(text) > 0:
            if text.startswith('-'):
                if len(text) == 1 or (len(text) == 2 and text[1] != '-'):
                    results = [opt + ' ' for opt in self.oneLetterOpts if opt.startswith(text)] + [None]
                elif len(text) >= 2 and text[1] == '-':
                    results = [opt + ' ' for opt in self.opts if opt.startswith(text)] + [None]
            else:
                results = [cmd + ' ' for cmd in self.cmds if cmd.startswith(text)] + [None]
    
        elif (len(tokens) == 1 and len(text) == 0) or len(tokens) > 1 :
            # only one rule for now: if an option of any sort (- or -- type) is present, you can only add another option,
            # not any commands
            if tokens[0] in self.oneLetterOpts + self.opts:
                oneLetterOpts = self.oneLetterOpts[:]
                opts = self.opts[:]
                for token in tokens[:-1]:
                    try:
                        oneLetterOpts.remove(token)
                    except ValueError:
                        pass
                    try:
                        opts.remove(token)
                    except ValueError:
                        pass
                results = [opt + ' ' for opt in oneLetterOpts + opts  if opt.startswith(text)] + [None]

        return results[state]

    """
    def completeTest(self, text, state):
        tokens = readline.get_line_buffer().split()
        file.write(text)
        file.write("TOKENS: " + repr(tokens))
        if len(tokens) == 0:
            results = [cmd for cmd in self.cmds if cmd.startswith(text)] + [None]
        elif len(tokens) == 1 and len(text)> 0:
            if text.startswith('-') and len(text) in [1,2]:
                file1.write(text)
                results = [opt + ' ' for opt in self.oneLetterOpts if opt.startswith(text)] + [None]
            elif text.startswith('--'):
                results = [opt + ' ' for opt in self.opts if opt.startswith(text)] + [None]
            else: 
                file2.write(str(len(text)))
                file2.write(text)
                results = [cmd + ' ' for cmd in self.cmds if cmd.startswith(text)] + [None]
        elif (len(tokens) == 1 and len(text) == 0) or len(tokens) > 1:
            if tokens[0] in self.cmds:
                results = [None]
            else:
                oneLetterOpts = self.oneLetterOpts[:]
                opts = self.opts[:]
                for token in tokens[:-1]:
                    try:
                        oneLetterOpts.remove(token)
                        opts.remove(token)
                    except ValueError:
                        pass

                results = oneLetterOpts + opts

        #file4.write(readline.get_line_buffer())
        delims = readline.get_completer_delims()
        file4.write(str(type(delims)))
        #readline.insert_text('allo')
        file4.write(str(results[state]))
        
        return results[state]
    """

readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))
readline.set_completer(PXRetransCompleter().complete)

if __name__ == '__main__':
    import readline, sys

    if sys.version[:1] < '3' :
       input = raw_input

    file = open('tano', 'a')
    file1 = open('tano1', 'a')
    file2 = open('tano2', 'a')
    file3 = open('tano3', 'a')
    file4 = open('tano4', 'a')

    pxrc = PXRetransCompleter()
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))
    readline.set_completer(pxrc.complete)
    input("prompt> ")

    file.close()
    file1.close()
    file2.close()
    file3.close()
    file4.close()
