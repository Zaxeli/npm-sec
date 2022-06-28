#! /usr/bin/python3

"""
Reference: 
Nikolai Tschacher's thesis, "Typosquatting in Programming Language PackageManagers", pp 17
https://incolumitas.com/data/thesis.pdf
"""

# TODO: extend to accomodate typo radius > 1
# so it won't be exact copy paste

class TypoRadius:

    def generate_typos(self, s):
        """
        Generates typos with edit distance 1 for string s
        """

        results = set()

        for i, char in enumerate(s):
            results.add(self.delete_op(s, i))
            for j, _ in enumerate(s):
                results.add(self.insert_op(s, char, j))
                results.add(self.replace_op(s, i , j))
            results.add(self.insert_op(s, char, len(s))) # also add at the end of string

        return results

    def delete_op(self, s, i):
        """
        Deletes cchar at position i
        """
        return s[:i] + s[i+1:]

    def insert_op(self, s, char, j):
        """
        insert char at position j in string s
        """
        return s[:j] + char + s[j:]

    def replace_op(self, s, i ,j):
        """
        Swap characters at positions i and j in string s
        """
        
        l = list(s)
        t_i = s[i]
        t_j = s[j]
        l[i] = t_j
        l[j] = t_i

        return ''.join(l)



rad = TypoRadius()
assert('reqeust' in rad.generate_typos('request'))