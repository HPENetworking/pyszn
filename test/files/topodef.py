TOPOLOGY = """
# Environment
[virtual=none awesomeness=medium]

# Nodes
[shell=vtysh] sw1 sw2
[type=host] hs1
hs2

# Links
sw1:1 -- hs1:1
[attr1=2.1e2 attr2=-2.7e-1] sw1:a -- hs1:a
[attr1=1 attr2="lorem ipsum" attr3=(1, 3.0, "B")] sw1:4 -- hs2:a
"""


def ordp(c):
    """
    Helper that returns a printable binary data representation.
    """
    output = []

    for i in c:
        if (i < 32) or (i >= 127):
            output.append('.')
        else:
            output.append(chr(i))

    return ''.join(output)


def hexdump(p):
    """
    Return a hexdump representation of binary data.

    Usage:

    >>> from hexdump import hexdump
    >>> print(hexdump(
    ...     b'\\x00\\x01\\x43\\x41\\x46\\x45\\x43\\x41\\x46\\x45\\x00\\x01'
    ... ))
    0000   00 01 43 41 46 45 43 41  46 45 00 01               ..CAFECAFE..
    """
    output = []
    l = len(p)
    i = 0
    while i < l:
        output.append('{:04d}   '.format(i))
        for j in range(16):
            if (i + j) < l:
                byte = p[i + j]
                output.append('{:02X} '.format(byte))
            else:
                output.append('   ')
            if (j % 16) == 7:
                output.append(' ')
        output.append('  ')
        output.append(ordp(p[i:i + 16]))
        output.append('\n')
        i += 16
    return ''.join(output)
