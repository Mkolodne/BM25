#Some code from https://github.com/nhirakawa/BM25/tree/master/src

import pandas as pd
import math
import operator


class InvertedIndex:
    def __init__(self):
        self.index = {}

    def __contains__(self, item):
        return item in self.index

    def __getitem__(self, item):
        return self.index[item]

    def add(self, word, docid):
        if word in self.index:
            if docid in self.index[word]:
                self.index[word][docid] += 1
            else:
                self.index[word][docid] = 1
        else:
            newdict = dict()
            newdict[docid] = 1
            self.index[word] = newdict
    def get_df(self, word):
        return len(self.index[word])

    def get_if(self, word):
        return len(self.index[word])

    
class DocumentLengthTable:
    def __init__(self):
        self.table = dict()

    def __len__(self):
        return len(self.table)
    
    def add(self, docid, length):
        self.table[docid] = length

    def get_length(self, docid):
        return self.table[docid]

    def get_average_length(self):
        return float(sum(list(self.table.values()))) / float(len(self.table))
        

    
class BM25:
    def __init__(self, filenames):
        self._df = self.__build_dataframe__(filenames)
        self._queries = self._df['title']
        self._passages = self._df['text']
        self._idx = InvertedIndex()
        self._dlt = DocumentLengthTable()
        self._corpus = dict()
        self.__build_corpus__()
        self.__build_struct__()
        
    def __build_dataframe__(self, filenames):
        frames = []
        for name in filenames:
            frames.append(pd.read_json(name))
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.loc[combined['type'] == 'question']
        return combined

    def __build_struct__(self):
        for docid in self._corpus:
            for word in self._corpus[docid]:
                self._idx.add(str(word), str(docid))
            length = len(self._corpus[str(docid)])
            self._dlt.add(docid, length)

    def __build_corpus__(self):
        for index in self._passages.index:
            curpass = self._passages.loc[index]
            curpass = curpass.strip().replace('\n', ' ').replace(',', ' ').lower().split(' ')
            curpass = [value for value in curpass if value != '']
            self._corpus[str(index)] = curpass

    def __score_BM25__(self, N, df, Freq, dl, avdl):
        k = 0.9
        b = 0.4
        IDF = math.log(1 + (N - df + 0.5) / (df + 0.5))
        TF = (Freq * (k + 1)) / (Freq + k * (1 - b + (b * dl / avdl)))
        BM25 = IDF * TF
        return BM25

    def __run_cleaned__(self, query):
        query_result = dict()
        for term in query:
            if term in query:
                doc_dict = self._idx[term]
                for docid, freq in doc_dict.items():
                    score = self.__score_BM25__(N=len(self._dlt), df = len(doc_dict), Freq = freq,
                                       dl = self._dlt.get_length(docid), avdl = self._dlt.get_average_length())
                    if docid in query_result:
                        query_result[docid] += score
                    else:
                        query_result[docid] = score
        return query_result

    def run(self, query, k):
        final = []
        cleaned = query.strip().replace('\n', ' ').replace(',', ' ').lower().split(' ')
        cleaned = [value for value in cleaned if value != '']
        result = self.__run_cleaned__(cleaned)
        sorted_x = sorted(result.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        for i in sorted_x[:k]:
            cur = dict()
            ID = i[0]
            cur['ID'] = ID
            cur['BM25'] = i[1]
            cur['Question'] = self._queries.loc[int(ID)] + '\n' + self._passages.loc[int(ID)]
            answer_dict = self._df.loc[int(ID)]['answers'][0]
            cur['answer'] = answer_dict['text']
            cur['date'] = answer_dict['created_at']
            cur['url'] = answer_dict['url']
            final.append(cur)
        return final
        
            
            
    
