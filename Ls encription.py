def encript1(string) :
    encr = dict()
    medium = list()
    
    encr['a'] = 'd'
    encr['s'] = 'f'
    encr['d'] = 'g'
    encr['f'] = 'h'
    encr['g'] = 'j'
    encr['h'] = 'k'
    encr['j'] = 'l'
    encr['k'] = 'a'
    encr['l'] = 's'

    encr['z'] = 'c'
    encr['x'] = 'v'
    encr['c'] = 'b'
    encr['v'] = 'n'
    encr['b'] = 'm'
    encr['n'] = 'z'
    encr['m'] = 'x'

    encr['q'] = 'e'
    encr['w'] = 'r'
    encr['e'] = 't'
    encr['r'] = 'y'
    encr['t'] = 'u'
    encr['y'] = 'i'
    encr['u'] = 'o'
    encr['i'] = 'p'
    encr['o'] = 'q'
    encr['p'] = 'w'    

    encr[' '] = ' '
    for char in raw :
        proc = encr[char]
        medium.append(proc)
    res = ''.join(medium)
    return res


raw = input('input : ')
method = input('method : ')
if method == '1':
    encrypt1(raw)









