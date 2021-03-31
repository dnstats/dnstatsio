import publicsuffix2
import collections

def main():
    with open('mx_records.txt', 'r') as f:
        domains = dict()
        for line in f:
            line = line.replace("{", '').replace('}', '').strip()
            name_servers = line.split(',')
            for name_server in name_servers:
                dom = publicsuffix2.get_public_suffix(name_server)
                if domains.__contains__(dom):
                    domains[dom] += 1
                else:
                    domains[dom] = 1

        od = collections.OrderedDict(sorted(domains.items()))
        
        with open('dnstats2.csv', 'w') as out:
            for dom in od:
                out.write("{},{},\n".format(dom, od.get(dom)))
                print(dom, od.get(dom))

        



if __name__ == '__main__':
    main()
