import pickle
import numpy as np
import re


class NumberSpellChecker(object):
    def __init__(self, base_symspell, D_correction):
        self.base_spell_numbers = base_symspell["base_spell_numbers"]

        self.prefix_spell_numbers = base_symspell["prefix_spell_numbers"]

        self.base_spell_fractions = base_symspell["base_spell_fractions"]

        self.suffix_spell_numbers = base_symspell["suffix_spell_numbers"]

        self.D = {**self.prefix_spell_numbers, **self.base_spell_numbers, **self.suffix_spell_numbers,
                  **self.base_spell_fractions}
        D_correction["ogtavos"] = "octavos"
        D_correction["otavos"] = "octavos"
        self.D_correction = D_correction

        self.init_prob()

        self.vocab = set(self.D.keys()).union(set(self.D_correction.keys())).difference(
            set("umo, sis, se, si, de, di, te, dis, des, cen, sisi, dez, cin, sen, nil, avo, ses, sin, tes, diz, sie".split(
                ", ")))

        self.maxlen = max(len(v) for v in self.vocab)

    def get_transcription(self, e):
        te = e.split()
        if len(te)==0:
            return e
        else:
            frac = False
            avos = False
            # print(te)
            #         print(e, te[-1])
            if "avos"==te[-1]:
                frac = True
                avos = True
                te = te[:-1] if len(te)>1 else ["un"]+te
            elif te[-1] in self.base_spell_fractions.keys():
                frac = True
                frac_b = self.base_spell_fractions[te[-1]]
                te = te[:-1] if len(te)>1 else ["un"]+te
                # print(te)
            if te[0] in self.D.keys():
                n = ""
                if len(te) > 1:
                    w0 = te[0]
                    m0 = int(w0 in self.prefix_spell_numbers.keys()) - int(w0=="mil")
                    n0 = self.D[w0]
                    cn = n0
                    for w in te[1:]:
                        m1 = int(w in self.prefix_spell_numbers.keys()) - int(w=="mil")
                        n1 = self.D[w]
                        if m0==0:
                            if m1==0:
                                if len(str(n1)) >= len(str(n0)) or n0==100:
                                    n += str(cn) + " "
                                    cn = n1
                                else:
                                    cn += n1
                            elif m1==1:
                                if (w0[-1]=="s") and (w[-1]=="i"):
                                    cn += n1
                                else:
                                    n += str(cn) + " "
                                    cn = n1
                            elif m1==-1:
                                cn = cn * n1

                        elif (m0==1) and (m1 in [1, -1]):
                            return e
                        elif (m0==1 and m1==0):
                            if len(str(n1)) >= len(str(n0)):
                                n += str(cn) + " "
                                cn = n1
                            else:
                                cn += n1
                        elif (m0==-1):
                            cn += n1

                        m0 = m1
                        w0 = w
                        n0 = n1
                    n += str(cn)
                else:
                    n = str(self.D[te[0]])
                if not frac:
                    return n
            if frac:
                try:
                    if avos:
                        a, b = n.split()
                        return f"{a}/{b}"
                    else:
                        a = n.split()[0]
                        return f"{a}/{frac_b}"
                except:
                    return e
            else:
                return e

    def init_prob(self):
        dic_prob_D = {w: np.log(f + 2) for w, f in self.D.items()}

        ND = sum(dic_prob_D.values())

        self.prob_D = {w: p / ND for w, p in dic_prob_D.items()}

        self.mp = min(self.prob_D.values())

        self.Mp = max(self.prob_D.values())

    def get_score(self, s, ixs):
        w1 = self.prob_D
        o = 0
        tokens = []
        for k in range(len(ixs) - 1):
            i, j = ixs[k], ixs[k + 1]
            t = s[i:j]
            if t in self.vocab:
                if t in self.D_correction.keys():
                    t = self.D_correction[t]
            tokens.append(t)
        l = " ".join(tokens)
        # mp = self.mp
        # Mp = self.Mp

        o += w1[tokens[0]] if tokens[0] in w1.keys() else 0
        for k in range(len(tokens) - 1):
            s = tokens[k + 1]
            v = 1
            if s in w1.keys():
                v = w1[s]
            else:
                v = 0
            o *= v
        return o, l

    def do(self, s0):
        #         print(s)
        start, s, pivs = self.get_prepross(s0)
        #         print(start, s)
        if start:
            ix = pivs[0]
            return self.internal(s[ix:])
        else:
            return [[0, s0]], 0

    def internal(self, s):
        o = []
        p = [[0]]
        b = 0
        lmax = 0
        for j in range(1, len(s) + 1):
            imax = -1
            p.append(p[-1] + [j])
            ascore = -1
            al = ""
            for i in range(j):
                ixs = p[i] + [j]
                nscore, nl = self.get_score(s, ixs)
                #                 print(j, nscore, nl, lmax)
                if nscore > ascore:
                    imax = i
                    ascore = nscore
                    al = nl
            p[j] = p[imax] + [j]
            o.append((ascore, al))
            if ascore > 0:
                b = j - 1
                lmax = 0
            #                 print(ascore, al, j-b-1)
            lj = j - b - 1
            if lj > lmax:
                lmax = lj
            #                 print(ascore, al, j-b-1, lmax, lj)
            if lmax > self.maxlen:
                break
        return o, b

    def get_prepross(self, s):
        tresholds = {2: 0.6, 5: 0.389, 3: 0.69}
        ns = str(s).strip().lower().replace("y", "i").replace("b", "v")  # .replace(" ", "")

        ix_per_token = {}
        current = 0
        t_ns = ns.split()
        for k, t in enumerate(t_ns):
            for _ in range(len(t)):
                ix_per_token[current + _] = k
            current += len(t)

        ns = "".join(t_ns)
        ix0 = len(ns)
        #         d0 = ""
        ln0 = 0
        rt = 0
        pivs = []
        for d in self.vocab:
            ixs = [match.start() for match in re.finditer(d, ns)]
            for ix in ixs:
                ln = len(d)
                rt = ln / sum(len(t_ns[t]) for t in {ix_per_token[ix], ix_per_token[ix + ln - 1]})
                tresh = 0.286 * int(ln <= 5) if ln not in tresholds.keys() else tresholds[ln]
                #                 if ((ix<ix0) and (rt>tresh))or((ix==ix0) and (rt>=rt0>tresh)):
                #                 print(rt, tresh, ix, d)
                if rt > tresh:
                    #                     print(ix, d)
                    pivs.append(ix)
                    if ix <= ix0:
                        #                     d0 = d
                        ln0 = ln
                        #                     rt0 = rt
                        ix0 = ix

                    #                     t0 = ix_per_token[ix0]
        #                     tf = ix_per_token[ix0+len(d0)-1]
        #                     print(ix0, d0,len(d0),len(d0)/sum(len(t_ns[t]) for t in {t0, tf}))
        if len(pivs)==0:
            return False, s, None
        else:
            return True, ns, sorted(pivs)

    def get_best(self, string):
        o, b = self.do(string)
        return o[b][1]

    def multi_do(self, s0):
        start, s, pivs = self.get_prepross(s0)
        global_o = []
        #         print(pivs)
        if start:
            while start:
                ix = pivs[0]
                o, b = self.internal(s[ix:])
                #                 print(o, b)
                global_o.append([ix, o, b])
                pivs = [jx for jx in pivs if jx > ix + b]
                start = pivs!=[]
            return global_o
        else:
            return [[0, [[0, s0]], 0]]

    def multi_get_best(self, string):
        global_o = self.multi_do(string)
        r = []
        for ix, o, b in global_o:
            #             print(ix, o, b)
            r.append([ix, o[b][1], b])
        return r

    def find(self, string):
        return self.get_transcription(self.get_best(string))

    def multi_find(self, string):
        r = []
        for ix, best, b in self.multi_get_best(string):
            r.append([ix, self.get_transcription(best), b])
        return r

    def apply(self, string):
        found = self.multi_find(string)
        first = found[0]
        #         print(first)
        if first[-1] > 0:
            ns = str(string).replace("\n", " ").strip()
            t_ns = ns.split()
            current_len = 0
            pivs = [0]
            for t in t_ns:
                current_len += len(t)
                pivs.append(current_len)
            r = ""
            bs = ns.replace(" ", "")
            comm = 0
            left = 0
            for ix, num, b in found:
                r += bs[comm: ix] + num
                #                 print(bs[comm: ix])
                #                 print(ix, pivs)
                #                 npivs = [ix+left]
                gap = len(num) - b - 1
                npivs = [ix + left]
                for p in pivs:
                    #                     print(p, gap,  p>ix, p+gap, 0<p-ix-left<b+1)
                    if 0 < p - ix - left < b + 1:
                        p = 0
                    elif p > ix + left:
                        p += gap
                    npivs.append(p)

                pivs = sorted(list(set(npivs + [ix + left + len(num)])))
                #                 nr = ""
                #                 for k in range(len(pivs)-1):
                #                     p0, p1 = pivs[k], pivs[k+1]
                #                     nr+=r[p0:p1]+" "
                #                 print(nr)
                comm = ix + b + 1
                left += gap

            r += bs[comm:]
            #

            pivs = sorted(pivs)
            nr = ""
            for k in range(len(pivs) - 1):
                p0, p1 = pivs[k], pivs[k + 1]
                nr += r[p0:p1] + " "

            return nr.strip()
        #             for ix, num, b in found:

        else:
            return string


if __name__ == "__main__":
    # base_symspell = {
    #     "base_spell_numbers": base_spell_numbers,
    #     "suffix_spell_numbers": suffix_spell_numbers,
    #     "prefix_spell_numbers": prefix_spell_numbers,
    #     "base_spell_fractions": base_spell_fractions,

    # }
    # pickle.dump(base_symspell, open("base_symspell.pickle", "wb"))
    base_symspell = pickle.load(open("base_symspell.pickle", "rb"))
    # pickle.dump(D_correction, open("D_correction.pickle", "wb"))
    D_correction = pickle.load(open("D_correction.pickle", "rb"))

    ws = NumberSpellChecker(base_symspell, D_correction)

    print(ws.find("      ")) # dies cinco > 10 5, y me dio ? #add memory len("sinco")/len("sin comer")# y me dio > 1/2? solo medio (*) sin comer > 5 mer?