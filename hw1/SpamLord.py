import sys
import os
import re
import pprint
from io import open

#my_first_pat = '(\w+)@(\w+).edu'
email_pat_1 = '([\w.-]+)(?: *)(?:@|where)(?: *)([\w.-]+)(?: *)(?:dom|dt|dot|\.)(?: *)(edu|com|org)'
email_pat_2 = '([\w.-]+)(?: +)(?:at)(?: +)([\w.-]+)(?: +)(?:dom|dt|dot)(?: +)(edu|com|org)'
email_pat_3 = '([\w.-]+)(?: +)(?:@|at|WHERE)(?: +)([\w]+)(?: *)(?:dot|;|\.)(?: *)([\w]+)(?: *)(?:dot|;|\.)(?: *)(edu|org|com)'
email_pat_4 = '([\w.-]+)(?:&#x40;)([\w]+)(?: *)(?:dot|;|\.)(?: *)([\w]+)(?: *)(?:dot|;|\.)(?: *)(edu|org|com)'
email_pat_5 = '([\w.-]+)(?: *)(?:\(followed by (?:&ldquo;|"))(?:@|where)(?: *)([\w.-]+)(?: *)(?:dom|dt|\.)(?: *)(edu|com|org)(?:(?:&rdquo;|")\))'
email_pat_6 = '([\w.-]+)(?: +)(?:@|at|where)(?: +)([\w]+)(?: +)([\w]+)(?: +)(edu|org|com)'
email_pat_7 = 'obfuscate\(\'([\w.-]+)\',\'(\w+)\'\)'
email_pat_8 = '((?:\w-)+)@((?:-\w)+-)\.((?:-\w)+)' 
phone_pat_1 = '(?:\(| ?)(\d{3})(?:\)| ?)(?:-| )(\d{3})(?:-| )(\d{4})'
phone_pat_2 = '(?:\()(\d{3})(?:\))(?: ?)(\d{3})-(\d{4})'

def process_file(name, f):
    """
    TODO
    This function takes in a filename along with the file object (actually
    a StringIO object at submission time) and
    scans its contents against regex patterns. It returns a list of
    (filename, type, value) tuples where type is either an 'e' or a 'p'
    for e-mail or phone, and value is the formatted phone number or e-mail.
    The canonical formats are:
         (name, 'p', '###-###-#####')
         (name, 'e', 'someone@something')
    If the numbers you submit are formatted differently they will not
    match the gold answers

    NOTE: ***don't change this interface***, as it will be called directly by
    the submit script

    NOTE: You shouldn't need to worry about this, but just so you know, the
    'f' parameter below will be of type StringIO at submission time. So, make
    sure you check the StringIO interface if you do anything really tricky,
    though StringIO should support most everything.
    """
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        matches = re.findall(email_pat_1,line, re.IGNORECASE)
        for m in matches:
            if m[0].lower() != "server":
                email = '%s@%s.%s' % m
                res.append((name,'e',email))
        matches = re.findall(email_pat_2,line, re.IGNORECASE)
        for m in matches:
            if m[0].lower() != "server":
                email = '%s@%s.%s' % m
                res.append((name,'e',email))
        matches = re.findall(email_pat_3,line, re.IGNORECASE)
        for m in matches:
            if m[0].lower() != "server":
                email = '%s@%s.%s.%s' % m
                res.append((name,'e',email))
        matches = re.findall(email_pat_4,line, re.IGNORECASE)
        for m in matches:
            if m[0].lower() != "server":
                email = '%s@%s.%s.%s' % m
                res.append((name,'e',email))
        matches = re.findall(email_pat_5,line, re.IGNORECASE)
        for m in matches:
            if m[0].lower() != "server":
                email = '%s@%s.%s' % m
                res.append((name,'e',email))
        matches = re.findall(email_pat_6,line, re.IGNORECASE)
        for m in matches:
            if m[0].lower() != "server" and m[2].lower() not in ('dt', 'dom', 'dot'):
                email = '%s@%s.%s.%s' % m
                res.append((name,'e',email))
        matches = re.findall(email_pat_7,line, re.IGNORECASE)
        for m in matches:
            if m[1].lower() != "server":
                email = '{}@{}'.format(m[1], m[0])
                res.append((name,'e',email))
        matches = re.findall(email_pat_8,line, re.IGNORECASE)
        for m in matches:
            ename = ''.join(m[0].split('-'))
            sname = ''.join(m[1].split('-'))
            dname = ''.join(m[2].split('-'))
            email = '{}@{}.{}'.format(ename, sname, dname)
            res.append((name,'e', email))
        matches = re.findall(phone_pat_1,line, re.IGNORECASE)
        for m in matches:
            phone = '%s-%s-%s' % m
            res.append((name,'p',phone))
        matches = re.findall(phone_pat_2,line, re.IGNORECASE)
        for m in matches:
            phone = '%s-%s-%s' % m
            res.append((name,'p',phone))
    return res


def process_dir(data_path):
    """
    You should not need to edit this function, nor should you alter
    its interface as it will be called directly by the submit script
    """
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path, fname)
        f = open(path, 'r', encoding='ISO-8859-1')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list


def get_gold(gold_path):
    """
    You should not need to edit this function.
    Given a path to a tsv file of gold e-mails and phone numbers
    this function returns a list of tuples of the canonical form:
    (filename, type, value)
    """
    # get gold answers
    gold_list = []
    f_gold = open(gold_path, 'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list


def score(guess_list, gold_list):
    """
    You should not need to edit this function.
    Given a list of guessed contacts and gold contacts, this function
    computes the intersection and set differences, to compute the true
    positives, false positives and false negatives.  Importantly, it
    converts all of the values to lower case before comparing
    """
    guess_list = [
        (fname, _type, value.lower())
        for (fname, _type, value)
        in guess_list
    ]
    gold_list = [
        (fname, _type, value.lower())
        for (fname, _type, value)
        in gold_list
    ]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    # print('Guesses (%d): ' % len(guess_set))
    # pp.pprint(guess_set)
    # print('Gold (%d): ' % len(gold_set))
    # pp.pprint(gold_set)
    print('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print('Summary: tp=%d, fp=%d, fn=%d' % (len(tp), len(fp), len(fn)))


def main(data_path, gold_path):
    """
    You should not need to edit this function.
    It takes in the string path to the data directory and the
    gold file
    """
    guess_list = process_dir(data_path)
    gold_list = get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('usage:\tSpamLord.py <data_dir> <gold_file>')
        sys.exit(0)
    main(sys.argv[1], sys.argv[2])