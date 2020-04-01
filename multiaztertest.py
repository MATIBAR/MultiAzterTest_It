#!/usr/bin/env python
# coding: utf-8

# In[29]:
import math
import os
import subprocess
import sys
from pathlib import Path
import csv
import stanfordnlp
from cube.api import Cube
import numpy as np
from collections import defaultdict
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
# genera CADENAS aleatorias
import uuid
#wordnet
nltk.download('wordnet')
#Add multilingual wordnet
nltk.download('omw')
from nltk.corpus import wordnet as wn
from nltk.corpus import cmudict
from scipy import spatial
from wordfreq import zipf_frequency
#####Argumentos##################################
from argparse import ArgumentParser
import pandas as pd
import pickle
from sklearn.externals import joblib
from gensim.models import FastText, KeyedVectors


# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class ModelAdapter:

    def __init__(self, model, lib):
        # parser
        self.model = model
        # model_name
        self.lib = lib

    def model_analysis(self, text, language):
        d = Document(text, language)  # ->data = []
        if self.lib == "stanford":
            lines = text.split('@')
            for line in lines:  # paragraph
                p = Paragraph()  # -> paragraph = []
                p.text = line
                if not line.strip() == '':
                    doc = self.model(line)
                    for sent in doc.sentences:
                        s = Sentence()
                        sequence = self.sent2sequenceStanford(sent)
                        # print(sequence)
                        s.text = sequence
                        for word in sent.words:
                            # Por cada palabra de cada sentencia, creamos un objeto Word que contendra los attrs
                            w = Word()
                            w.index = str(word.index)
                            w.text = word.text
                            w.lemma = word.lemma
                            w.upos = word.upos
                            w.xpos = word.xpos
                            w.feats = word.feats
                            w.governor = word.governor
                            w.dependency_relation = word.dependency_relation
                            s.word_list.append(w)
                            # print(str(w.index) + "\t" + w.text + "\t" + w.lemma + "\t" + w.upos + "\t" + w.xpos + "\t" + w.feats + "\t" + str(w.governor) + "\t" + str(w.dependency_relation) +"\t")
                        p.sentence_list.append(s)  # ->paragraph.append(s)
                    d.paragraph_list.append(p)  # ->data.append(paragraph)

        elif self.lib == "cube":
            d = Document(text, language)  # ->data = []
            lines = text.split('@')
            for line in lines:
                p = Paragraph()  # -> paragraph = []
                p.text = line
                if not line.strip() == '':
                    sequences = self.model(line)
                    for seq in sequences:
                        s = Sentence()
                        sequence = self.sent2sequenceCube(seq)
                        s.text = sequence
                        for entry in seq:
                            # Por cada palabra de cada sentencia, creamos un objeto Word que contendra los attrs
                            w = Word()
                            w.index = str(entry.index)
                            w.text = entry.word
                            w.lemma = entry.lemma
                            w.upos = entry.upos
                            w.xpos = entry.xpos
                            w.feats = entry.attrs
                            w.governor = int(entry.head)
                            w.dependency_relation = str(entry.label)
                            s.word_list.append(w)
                            # print(str(
                            #     w.index) + "\t" + w.text + "\t" + w.lemma + "\t" + w.upos + "\t" + w.xpos + "\t" + w.feats + "\t" + str(
                            #     w.governor) + "\t" + str(w.dependency_relation) + "\t")
                        p.sentence_list.append(s)  # ->paragraph.append(s)
                    d.paragraph_list.append(p)  # ->data.append(paragraph)
        return d

    def sent2sequenceStanford(self, sent):
        conllword = ""
        for word in sent.words:
            conllword = conllword + " " + str(word.text)
        return conllword

    def sent2sequenceCube(self, sent):
        conllword = ""
        for entry in sent:
            conllword = conllword + " " + str(entry.word)
        return conllword


class Document:
    def __init__(self, text, language):
        self._text = text
        self.language = language
        self._paragraph_list = []
        self.words_freq = {}
        # Indicadores
        self.indicators = defaultdict(float)
        self.aux_lists = defaultdict(list)
        # Constantes
        self.WORD_FREQ_EN = 4
        self.WORD_FREQ_ES = 4
        self.WORD_FREQ_EU = 34

    @property
    def text(self):
        """ Access text of this document. Example: 'This is a sentence.'"""
        return self._text

    @text.setter
    def text(self, value):
        """ Set the document's text value. Example: 'This is a sentence.'"""
        self._text = value

    @property
    def paragraph_list(self):
        """ Access list of sentences for this document. """
        return self._paragraph_list

    @paragraph_list.setter
    def paragraph_list(self, value):
        """ Set the list of tokens for this document. """
        self._paragraph_list = value

    def get_indicators(self, similarity):
        self.calculate_all_numbers(similarity)
        self.calculate_all_means()
        self.calculate_all_std_deviations()
        self.calculate_all_incidence()
        self.calculate_density()
        self.calculate_all_overlaps()
        return self.indicators

    def create_dataframe(self):
        i = self.indicators
        indicators_dict = {}
        headers = []
        for key, value in i.items():
            indicators_dict[key] = i.get(key)
            headers.append(key)
        return pd.DataFrame(indicators_dict, columns=headers, index=[0])

    # self.indicators['num_words'] = self.calculate_num_words()
    #     def calculate_num_words(self):
    #         num_words = 0
    #         not_punctuation = lambda w: not (len(w.text) == 1 and (not w.text.isalpha()))
    #         for paragraph in self._paragraph_list:
    #             self.aux_lists['sentences_per_paragraph'].append(len(paragraph.sentence_list))  # [1,2,1,...]
    #             for sentence in paragraph.sentence_list:
    #                 filterwords = filter(not_punctuation, sentence.word_list)
    #                 sum = 0
    #                 for word in filterwords:
    #                     num_words += 1
    #                     self.aux_lists['words_length_list'].append(len(word.text))
    #                     self.aux_lists['lemmas_length_list'].append(len(word.lemma))
    #                     sum += 1
    #                 self.aux_lists['sentences_length_mean'].append(sum)
    #         return num_words

    #     def calculate_num_paragraphs(self):
    #         return len(self._paragraph_list)
    #    self.indicators['num_sentences'] = self.calculate_num_sentences()
    #    self.indicators['num_paragraphs'] = self.calculate_num_paragraphs()
    #     def calculate_num_sentences(self):
    #         num_sentences = 0
    #         for paragraph in self._paragraph_list:
    #             for sentence in paragraph.sentence_list:
    #                 num_sentences += 1
    #         return num_sentences

    def calculate_simple_ttr(self, p_diff_forms=None, p_num_words=None):
        if (p_diff_forms and p_num_words) is not None:
            return (len(p_diff_forms)) / p_num_words
        else:
            self.indicators['simple_ttr'] = round(self.indicators['num_different_forms'] / self.indicators['num_words'],
                                                  4)

    def calculate_nttr(self):
        if self.indicators['num_noun'] > 0:
            self.indicators['nttr'] = round(len(self.aux_lists['different_nouns']) / self.indicators['num_noun'], 4)

    def calculate_ratio_proper_nouns_per_nouns(self):
        if self.indicators['num_proper_noun'] > 0:
            self.indicators['ratio_proper_nouns_per_nouns'] = round(
                self.indicators['num_proper_noun'] / (self.indicators['num_noun'] +
                                                      self.indicators['num_proper_noun']), 4)

    def calculate_vttr(self):
        if self.indicators['num_verb'] > 0:
            self.indicators['vttr'] = round(len(self.aux_lists['different_verbs']) / self.indicators['num_verb'], 4)

    def calculate_adj_ttr(self):
        if self.indicators['num_adj'] > 0:
            self.indicators['adj_ttr'] = round(len(self.aux_lists['different_adjs']) / self.indicators['num_adj'], 4)

    def calculate_adv_ttr(self):
        if self.indicators['num_adv'] > 0:
            self.indicators['adv_ttr'] = round(len(self.aux_lists['different_advs']) / self.indicators['num_adv'], 4)

    def calculate_content_ttr(self):
        nttr = self.indicators['nttr']
        vttr = self.indicators['vttr']
        adj_ttr = self.indicators['adj_ttr']
        adv_ttr = self.indicators['adv_ttr']
        self.indicators['content_ttr'] = round((nttr + vttr + adj_ttr + adv_ttr) / 4, 4)

    def calculate_all_ttr(self):
        self.calculate_simple_ttr()
        self.calculate_nttr()
        self.calculate_vttr()
        self.calculate_adj_ttr()
        self.calculate_adv_ttr()
        self.calculate_content_ttr()

    def calculate_lemma_ttr(self):
        self.indicators['lemma_ttr'] = round(len(self.aux_lists['different_lemmas']) / self.indicators['num_words'], 4)

    def calculate_lemma_nttr(self):
        if self.indicators['num_noun'] > 0:
            self.indicators['lemma_nttr'] = round(
                len(self.aux_lists['different_lemma_nouns']) / self.indicators['num_noun'], 4)

    def calculate_lemma_vttr(self):
        if self.indicators['num_verb'] > 0:
            self.indicators['lemma_vttr'] = round(
                len(self.aux_lists['different_lemma_verbs']) / self.indicators['num_verb'], 4)

    def calculate_lemma_adj_ttr(self):
        if self.indicators['num_adj'] > 0:
            self.indicators['lemma_adj_ttr'] = round(
                len(self.aux_lists['different_lemma_adjs']) / self.indicators['num_adj'], 4)

    def calculate_lemma_adv_ttr(self):
        if self.indicators['num_adv'] > 0:
            self.indicators['lemma_adv_ttr'] = round(
                len(self.aux_lists['different_lemma_advs']) / self.indicators['num_adv'], 4)

    def calculate_lemma_content_ttr(self):
        lnttr = self.indicators['lemma_nttr']
        lvttr = self.indicators['lemma_vttr']
        ladj_ttr = self.indicators['lemma_adj_ttr']
        ladv_ttr = self.indicators['lemma_adv_ttr']
        self.indicators['lemma_content_ttr'] = round((lnttr + lvttr + ladj_ttr + ladv_ttr) / 4, 4)

    def calculate_all_lemma_ttr(self):
        self.calculate_lemma_ttr()
        self.calculate_lemma_nttr()
        self.calculate_lemma_vttr()
        self.calculate_lemma_adj_ttr()
        self.calculate_lemma_adv_ttr()
        self.calculate_lemma_content_ttr()

    def get_ambiguity_level(self, word, FLAG, wn_lang):
        if FLAG == 'NOUN':
            ambiguity_level = len(wn.synsets(word, pos='n', lang=wn_lang))
        elif FLAG == 'ADJ':
            ambiguity_level = len(wn.synsets(word, pos='a', lang=wn_lang))
        elif FLAG == 'ADV':
            ambiguity_level = len(wn.synsets(word, pos='r', lang=wn_lang))
        else:
            ambiguity_level = len(wn.synsets(word, pos='v', lang=wn_lang))
        return ambiguity_level

    def get_abstraction_level(self, word, FLAG, wn_lang):
        abstraction_level = 0
        if len(wn.synsets(word, pos=FLAG, lang=wn_lang)) > 0:
            abstraction_level = len(wn.synsets(word, pos=FLAG, lang=wn_lang)[0].hypernym_paths()[0])
        return abstraction_level

    def calculate_mean_depth_per_sentence(self, depth_list):
        i = self.indicators
        i['mean_depth_per_sentence'] = round(float(np.mean(depth_list)), 4)

    def tree_depth(self, tree, root):
        if not tree[root]:
            return 1
        else:
            return 1 + max(self.tree_depth(tree, int(x)) for x in tree[root])

    def mtld(self, filtered_words):
        ttr_threshold = 0.72
        ttr = 1.0
        word_count = 0
        fragments = 0.0
        dif_words = []
        for i, word in enumerate(filtered_words):
            word = word.lower()
            word_count += 1
            if word not in dif_words:
                dif_words.append(word)
            ttr = self.calculate_simple_ttr(dif_words, word_count)
            if ttr <= ttr_threshold:
                fragments += 1
                word_count = 0
                dif_words.clear()
                ttr = 1.0
            elif i == len(filtered_words) - 1:
                residual = (1.0 - ttr) / (1.0 - ttr_threshold)
                fragments += residual

        if fragments != 0:
            return len(filtered_words) / fragments
        else:
            return 0

    def calculate_mtld(self):
        not_punctuation = lambda w: not (len(w) == 1 and (not w.isalpha()))
        filtered_words = list(filter(not_punctuation, word_tokenize(self.text)))
        self.indicators['mtld'] = round((self.mtld(filtered_words) + self.mtld(filtered_words[::-1])) / 2, 4)

    # SMOG=1,0430*SQRT(30*totalcomplex/totalsentences)+3,1291 (total polysyllables --> con mas de 3 silabas)
    def calculate_smog(self):
        i = self.indicators
        ts = i['num_sentences']
        tps = i['num_words_more_3_syl']
        self.indicators['smog'] = round(1.0430 * math.sqrt(30 * tps / ts) + 3.1291, 4)

    def get_num_hapax_legomena(self):
        num_hapax_legonema = 0
        for word, frecuencia in self.words_freq.items():
            if frecuencia == 1:
                num_hapax_legonema += 1
        return num_hapax_legonema

    def calculate_honore(self):
        n = self.indicators['num_words']
        v = len(self.aux_lists['different_forms'])
        v1 = self.get_num_hapax_legomena()
        self.indicators['honore'] = round(100 * ((np.log10(n)) / (1 - (v1 / v))), 4)

    def calculate_maas(self):
        n = self.indicators['num_words']
        v = len(self.aux_lists['different_forms'])
        self.indicators['maas'] = round((np.log10(n) - np.log10(v)) / (np.log10(v) ** 2), 4)

    # Noun overlap measure is binary (there either is or is not any overlap between a pair of adjacent sentences in a text ).
    # Noun overlap measures the proportion of sentences in a text for which there are overlapping nouns,
    # With no deviation in the morphological forms (e.g., table/tables)
    # (número pares de sentencias adjacentes que tienen al menos algún nombre en común)/(Número de pares de sentencias adjacentes)
    def calculate_noun_overlap_adjacent(self):
        i = self.indicators
        adjacent_noun_overlap_list = []
        # paragraph_list es una lista de doc.sentences donde doc.sentences es una "lista de obj sentencias" de un parrafo=[doc.sentence1,...]
        for paragraph in self.paragraph_list:
            # Por cada parrafo:paragraph es "lista de obj sentencias" de un parrafo=[doc.sentence1,...]
            if len(paragraph.sentence_list) > 1:
                # zip Python zip function takes iterable elements as input, and returns iterator que es un flujo de datos que
                # puede ser recorrido por for o map.
                # Si paragraph = [[sentence1], [sentence2], [sentence3]]
                # paragraph[1:] = [[sentence2], [sentence3]]
                test = zip(paragraph.sentence_list, paragraph.sentence_list[1:])  # zip the values
                # print(test) #-><zip object at 0x7eff7b354c08>=?[([sentence1],[sentence2]),([sentence2],[sentence3]),...]
                # for values in test:
                # print(values)  # print each tuples
                # ([sentence1],[sentence2])
                # ([sentence2],[sentence3])
                # map aplica la función list a todos los elementos de zip y como resultado se devuelve un iterable de tipo map
                # funcion list=The list() constructor returns a mutable (the object can be modified) sequence list of elements.
                # Por cada valor de test genera una lista
                # print(testlist) #<map object at 0x7eff7b3701d0>=?[[([sentence1],[sentence2])],[([sentence2],[sentence3])]]
                adjacents = list(map(list, test))
                # print(type(adjacents))
                # print(adjacents) ##Ejm: Parrafo1:[[[sent1], [sent2]], [[sent2], [sent3]]] donde sentenceX es conllword1,conllword2,...
                for x in adjacents:
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x[0].word_list:
                        # values1 = entry1.split("\t")
                        if entry1.is_noun():
                            sentence1.append(entry1.text.lower())
                    for entry2 in x[1].word_list:
                        # values2 = entry2.split("\t")
                        if entry2.is_noun():
                            sentence2.append(entry2.text.lower())
                    # nombres en comun entre sentence1 y sentence2
                    in_common = list(set(sentence1).intersection(sentence2))
                    # si hay nombre en comun añado 1
                    if len(in_common) > 0:
                        adjacent_noun_overlap_list.append(1)
                    else:
                        adjacent_noun_overlap_list.append(0)
        if len(adjacent_noun_overlap_list) > 0:
            i['noun_overlap_adjacent'] = round(float(np.mean(adjacent_noun_overlap_list)), 4)

    # Noun overlap measures which is the average overlap between all pairs of sentences in the text for which there are overlapping nouns,
    # With no deviation in the morphological forms (e.g., table/tables)
    # (Sumatorio de todos pares de sentencias del texto que tienen alguna coincidencia en algún nombre)/(todos los pares de sentencias del texto)
    def calculate_noun_overlap_all(self):
        i = self.indicators
        all_noun_overlap_list = []
        for paragraph in self.paragraph_list:
            for index in range(len(paragraph.sentence_list)):
                similarity_tmp = paragraph.sentence_list[index + 1:]
                x = paragraph.sentence_list[index]
                for index2 in range(len(similarity_tmp)):
                    y = similarity_tmp[index2]
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x.word_list:
                        # values1 = entry1.split("\t")
                        if entry1.is_noun():
                            sentence1.append(entry1.text.lower())
                    for entry2 in y.word_list:
                        # values2 = entry2.split("\t")
                        if entry2.is_noun():
                            sentence2.append(entry2.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    if len(in_common) > 0:
                        all_noun_overlap_list.append(1)
                    else:
                        all_noun_overlap_list.append(0)
        if len(all_noun_overlap_list) > 0:
            i['noun_overlap_all'] = round(float(np.mean(all_noun_overlap_list)), 4)

    # Argument overlap measure is binary (there either is or is not any overlap between a pair of adjacent
    # sentences in a text ). Argument overlap measures the proportion of sentences in a text for which there are overlapping the
    # between nouns (stem, e.g., “table”/”tables”) and personal pronouns (“he”/”he”)
    def calculate_argument_overlap_adjacent(self):
        i = self.indicators
        adjacent_argument_overlap_list = []
        for paragraph in self.paragraph_list:
            if len(paragraph.sentence_list) > 1:
                adjacents = list(map(list, zip(paragraph.sentence_list, paragraph.sentence_list[1:])))
                for x in adjacents:
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x[0].word_list:
                        if entry1.is_personal_pronoun or entry1.is_noun():
                            sentence1.append(entry1.text.lower())
                    for entry2 in x[1].word_list:
                        if entry2.is_personal_pronoun or entry2.is_noun():
                            sentence2.append(entry1.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    if len(in_common) > 0:
                        adjacent_argument_overlap_list.append(1)
                    else:
                        adjacent_argument_overlap_list.append(0)
        if len(adjacent_argument_overlap_list) > 0:
            i['argument_overlap_adjacent'] = round(float(np.mean(adjacent_argument_overlap_list)), 4)

    # Argument overlap measures which is the average overlap between all pairs of sentences in the
    # text for which there are overlapping stem nouns and personal pronouns.
    def calculate_argument_overlap_all(self):
        i = self.indicators
        all_argument_overlap_list = []
        for paragraph in self.paragraph_list:
            for index in range(len(paragraph.sentence_list)):
                similarity_tmp = paragraph.sentence_list[index + 1:]
                x = paragraph.sentence_list[index]
                for index2 in range(len(similarity_tmp)):
                    y = similarity_tmp[index2]
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x.word_list:
                        if entry1.is_personal_pronoun or entry1.is_noun():
                            sentence1.append(entry1.text.lower())
                    for entry2 in y.word_list:
                        if entry2.is_personal_pronoun or entry2.is_noun():
                            sentence2.append(entry2.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    if len(in_common) > 0:
                        all_argument_overlap_list.append(1)
                    else:
                        all_argument_overlap_list.append(0)
        if len(all_argument_overlap_list) > 0:
            i['argument_overlap_all'] = round(float(np.mean(all_argument_overlap_list)), 4)

    # Stem overlap measure is binary (there either is or is not any overlap between a pair of adjacent sentences in a text ).
    # Stem overlap measures the proportion of sentences in a text for which there are overlapping between a noun in one
    # sentence and a content word (i['e.,'] nouns,verbs, adjectives, adverbs) in a previous sentence
    # that shares a common lemma (e.g., “tree”/”treed”;”mouse”/”mousey”).
    def calculate_stem_overlap_adjacent(self):
        i = self.indicators
        adjacent_stem_overlap_list = []
        for paragraph in self.paragraph_list:
            if len(paragraph.sentence_list) > 1:
                adjacents = list(map(list, zip(paragraph.sentence_list, paragraph.sentence_list[1:])))
                for x in adjacents:
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x[0].word_list:
                        if entry1.is_lexic_word(x[0]):
                            sentence1.append(entry1.text.lower())
                    for entry2 in x[1].word_list:
                        if entry2.is_noun():
                            sentence2.append(entry2.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    if len(in_common) > 0:
                        adjacent_stem_overlap_list.append(1)
                    else:
                        adjacent_stem_overlap_list.append(0)
        if len(adjacent_stem_overlap_list) > 0:
            i['stem_overlap_adjacent'] = round(float(np.mean(adjacent_stem_overlap_list)), 4)

    # Global Stem overlap measures which is the average overlap between all pairs of sentences in
    # the text for which there are overlapping Between a noun in one sentence and a content word
    # (i['e.,'] nouns,verbs, adjectives, adverbs) in a previous sentence that shares a common
    # lemma (e.g., “tree”/”treed”;”mouse”/”mousey”).
    def calculate_stem_overlap_all(self):
        i = self.indicators
        all_stem_overlap_list = []
        for paragraph in self.paragraph_list:
            for index in range(len(paragraph.sentence_list)):
                similarity_tmp = paragraph.sentence_list[index + 1:]
                x = paragraph.sentence_list[index]
                for index2 in range(len(similarity_tmp)):
                    y = similarity_tmp[index2]
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x.word_list:
                        if entry1.is_lexic_word(x):
                            sentence1.append(entry1.text.lower())
                    for entry2 in y.word_list:
                        if entry2.is_noun():
                            sentence2.append(entry2.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    if len(in_common) > 0:
                        all_stem_overlap_list.append(1)
                    else:
                        all_stem_overlap_list.append(0)
        if len(all_stem_overlap_list) > 0:
            i['stem_overlap_all'] = round(float(np.mean(all_stem_overlap_list)), 4)

    # Content word overlap adjacent sentences proporcional mean refers to the proportion of content words
    # (nouns, verbs,adverbs,adjectives, pronouns) that shared Between pairs of sentences.For example, if
    # a sentence pair has fewer words and two words overlap, The proportion is greater than if a pair has
    # many words and two words overlap. This measure may be particulaly useful when the lenghts of the
    # sentences in the text are principal concern.
    def calculate_content_overlap_adjacent(self):
        i = self.indicators
        adjacent_content_overlap_list = []
        for paragraph in self.paragraph_list:
            if len(paragraph.sentence_list) > 1:
                adjacents = list(map(list, zip(paragraph.sentence_list, paragraph.sentence_list[1:])))
                for x in adjacents:
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x[0].word_list:
                        if entry1.is_lexic_word(x[0]):
                            sentence1.append(entry1.text.lower())
                    for entry2 in x[1].word_list:
                        if entry2.is_lexic_word(x[1]):
                            sentence2.append(entry2.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    n1 = x[0].count_content_words_in()
                    n2 = x[1].count_content_words_in()
                    if n1 + n2 > 0:
                        adjacent_content_overlap_list.append(len(in_common) / (n1 + n2))
                    else:
                        adjacent_content_overlap_list.append(0)
        if len(adjacent_content_overlap_list) > 0:
            i['content_overlap_adjacent_mean'] = round(float(np.mean(adjacent_content_overlap_list)), 4)
            i['content_overlap_adjacent_std'] = round(float(np.std(adjacent_content_overlap_list)), 4)

    # Content word overlap adjacent sentences proporcional mean refers to the proportion of content words
    # (nouns, verbs,adverbs,adjectives, pronouns) that shared Between pairs of sentences.For example, if
    # a sentence pair has fewer words and two words overlap, The proportion is greater than if a pair has
    # many words and two words overlap. This measure may be particulaly useful when the lenghts of the
    # sentences in the text are principal concern.
    def calculate_content_overlap_all(self):
        i = self.indicators
        all_content_overlap_list = []
        for paragraph in self.paragraph_list:
            for index in range(len(paragraph.sentence_list)):
                similarity_tmp = paragraph.sentence_list[index + 1:]
                x = paragraph.sentence_list[index]
                for index2 in range(len(similarity_tmp)):
                    y = similarity_tmp[index2]
                    sentence1 = []
                    sentence2 = []
                    for entry1 in x.word_list:
                        if entry1.is_lexic_word(x):
                            sentence1.append(entry1.text.lower())
                    for entry2 in y.word_list:
                        if entry2.is_lexic_word(y):
                            sentence2.append(entry2.text.lower())
                    in_common = list(set(sentence1).intersection(sentence2))
                    n1 = x.count_content_words_in()
                    n2 = y.count_content_words_in()
                    if n1 + n2 > 0:
                        all_content_overlap_list.append(len(in_common) / (n1 + n2))
                    else:
                        all_content_overlap_list.append(0)
        if len(all_content_overlap_list) > 0:
            i['content_overlap_all_mean'] = round(float(np.mean(all_content_overlap_list)), 4)
            i['content_overlap_all_std'] = round(float(np.std(all_content_overlap_list)), 4)

    def calculate_all_overlaps(self):
        self.calculate_noun_overlap_adjacent()
        self.calculate_noun_overlap_all()
        self.calculate_argument_overlap_adjacent()
        self.calculate_argument_overlap_all()
        self.calculate_stem_overlap_adjacent()
        self.calculate_stem_overlap_all()
        self.calculate_content_overlap_adjacent()
        self.calculate_content_overlap_all()

    def flesch(self):
        flesch = 0
        sentences = float(self.indicators['num_sentences'])
        syllables = float(sum(self.aux_lists['syllables_list']))
        words = float(self.indicators['num_words'])
        # ranking scale of 0-100
        # For most business writing, a score of 65 is a good target, and scores between 60 and 80 should generally
        # be understood by 12 to 15 year olds.
        if self.language == "english" or self.language == "basque":
            # formula= 206.835 - 1.015 x (words/sentences) - 84.6 x (syllables/words)
            flesch = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        if self.language == "spanish":
            # Flesh=206.84 -60 * P - 1,02 F donde  P, el promedio de sílabas por palabra; F, la media de palabras por frase.
            flesch = 206.84 - 1.02 * (words / sentences) - 60 * (syllables / words)
        if flesch >= 0: self.indicators['flesch'] = round(flesch, 4)

    def flesch_kincaid(self):
        sentences = float(self.indicators['num_sentences'])
        syllables = float(sum(self.aux_lists['syllabes_list']))
        words = float(self.indicators['num_words'])
        # Flesch-Kincaid grade level formula = 0.39 x (words/sentences) + 11.8 x (syllables/words) - 15.59.
        # Years:American School Grade:European School Grade
        # 6-7:1:LH1
        # 7-8:2:LH2
        # 8-9:3:LH3
        # 9-10:4:LH4
        # 10-11:5:LH5
        # 11-12:6:LH6
        # 12-13:7:DBH1
        # 13-14:8:DBH2
        # 14-15:9:DBH3
        # 15-16:10:DBH4
        # 16-17:11:bachiller1
        # 17-18:12:bachiller2
        fk = 0.39 * words / sentences + 11.8 * syllables / words - 15.59
        if fk >= 0:
            self.indicators['flesch_kincaid'] = round(fk, 4)

    #def calculate_dale_chall(self):
    #    sentences = self.indicators['num_sentences']
    #    complex_words = self.indicators['num_complex_words']
    #    words = self.indicators['num_words']
    #    percentage = (complex_words / words) * 100
    #    if percentage >= 5.0:
    #        self.indicators['dale_chall'] = round(0.1579 * percentage + 0.0496 * (words / sentences) + 3.6365, 4)
    #    else:
    #        self.indicators['dale_chall'] = round(0.1579 * percentage + 0.0496 * (words / sentences), 4)

    def calculate_connectives_for(self, sentence, connectives):
        i = self.indicators
        list_a = []
        list_b = []
        num_a = 0
        num_b = 0
        text = sentence.text
        for x in connectives:
            if "*" in x:
                list_a.append(x)
            else:
                list_b.append(x)
        for a in list_a:
            split = a.split('*')
            matches_a = re.findall(r'\b%s\b[^.!?()]+\b%s\b' % (split[0], split[1]), text)
            num_a += len(matches_a)
        for b in list_b:
            matches_b = re.findall(r'\b%s\b' % b, text)
            num_b += len(matches_b)
        return num_a + num_b

    def calculate_readability(self):
        if self.language == "english":
            #self.calculate_dale_chall()
            self.flesch_kincaid()
            self.calculate_smog()
            self.flesch()
        if self.language == "spanish":
            self.flesch()


    def calculate_connectives_for(self, sentence, connectives):
        i = self.indicators
        list_a = []
        list_b = []
        num_a = 0
        num_b = 0
        text = sentence.text.lower()
        for x in connectives:
            if "*" in x:
                list_a.append(x)
            else:
                list_b.append(x)
        for a in list_a:
            split = a.split('*')
            matches_a = re.findall(r'\b%s\b[^.!?()]+\b%s\b' % (split[0], split[1]), text)
            num_a += len(matches_a)
        for b in list_b:
            matches_b = re.findall(r'\b%s\b' % b, text)
            num_b += len(matches_b)
        return num_a + num_b

    def calculate_connectives(self):
        i = self.indicators
        for p in self.paragraph_list:
            for s in p.sentence_list:
                i['causal_connectives'] += self.calculate_connectives_for(s, Connectives.causal)
                i['temporal_connectives'] += self.calculate_connectives_for(s, Connectives.temporal)
                i['conditional_connectives'] += self.calculate_connectives_for(s, Connectives.conditional)
                i['logical_connectives'] += self.calculate_connectives_for(s, Connectives.logical)
                i['adversative_connectives'] += self.calculate_connectives_for(s, Connectives.adversative)
        i['all_connectives'] = i['causal_connectives'] + i['temporal_connectives'] + i['conditional_connectives'] + \
                                   i['logical_connectives'] + i['adversative_connectives']

    def calculate_all_numbers(self, similarity):
        i = self.indicators
        i['num_paragraphs'] = len(self._paragraph_list)
        # i['num_words'] = 0
        # i['num_sentences'] = 0
        num_np_list = []
        num_vp_list = []
        modifiers_per_np = []
        depth_list = []
        min_wordfreq_list = []
        # subordinadas_labels = ['csubj', 'csubj:pass', 'ccomp', 'xcomp', 'advcl', 'acl', 'acl:relcl']
        decendents_total = 0
        text_without_punctuation = []
        # Wordnet config lang
        if self.language == "english":
            self.wn_lang = "eng"
        elif self.language == "basque":
            self.wn_lang = "eus"
        elif self.language == "spanish":
            self.wn_lang = "spa"
        if similarity:
            print("similarity")
            # Fasttext embbeding
            # fasttext erabili dut entrenatzeko eta Wikipedian entrenatuak
            # izan dira. IDF kontaketak ere wikipediatik atera dira.
            # @inproceedings{mikolov2018advances,
            #  title={Advances in Pre-Training Distributed Word Representations},
            #  author={Mikolov, Tomas and Grave, Edouard and Bojanowski, Piotr and Puhrsch, Christian and Joulin, Armand},
            #  booktitle={Proceedings of the International Conference on Language Resources and Evaluation (LREC 2018)},
            #  year={2018}
            # }
            self.num_features = 512
            if self.language == "english":
                self.model = KeyedVectors.load_word2vec_format('wordembeddings/orig2idf/en',
                                                               binary=False)
                self.index2word_set = set(self.model.wv.index2word)
            elif self.language == "basque":
                self.model = KeyedVectors.load_word2vec_format('wordembeddings/orig2idf/eu',
                                                               binary=False)
                self.index2word_set = set(self.model.wv.index2word)
            elif self.language == "spanish":
                self.model = KeyedVectors.load_word2vec_format('wordembeddings/orig2idf/es',
                                                               binary=False)
                self.index2word_set = set(self.model.wv.index2word)

        for p in self.paragraph_list:
            self.aux_lists['sentences_per_paragraph'].append(len(p.sentence_list))  # [1,2,1,...]
            sentencesPerParag = []
            for s in p.sentence_list:
                num_words_in_sentences = 0
                if not s.text == "":
                    self.aux_lists['sentences_in_text_token_list'].append(s)
                    # self.aux_lists['sentences_in_paragraph_list'].append(s)
                    sentencesPerParag.append(s)
                    num_words_in_sentence_without_stopwords = 0
                    i['num_sentences'] += 1
                    dependency_tree = defaultdict(list)
                    np_indexes = s.count_np_in_sentence()
                    num_np_list.append(len(np_indexes))
                    vp_indexes = s.count_vp_in_sentence()
                    num_vp_list.append(vp_indexes)
                    decendents_total += s.count_decendents(np_indexes)
                    modifiers_per_np += s.count_modifiers(np_indexes)
                    self.aux_lists['left_embeddedness'].append(s.calculate_left_embeddedness())
                    i['prop'] = 0
                    i['num_punct_in_sentence'] = 0
                    wordfreq_list = []
                    sum_s = 0
                    for w in s.word_list:
                        if w.is_punctuation():
                            i['num_punct_in_sentence'] += 1
                        if not w.is_punctuation():
                            i['num_words'] += 1
                            sum_s += 1
                            # Obtenemos el numero de silabas de cada palabra
                            text_without_punctuation.append(w)
                        if w.governor == 0:
                            root = w.index
                        dependency_tree[w.governor].append(w.index)
                        i['num_words_with_punct'] += 1
                        # word frequency
                        if (not len(w.text) == 1 or w.text.isalpha()) and not w.is_num():
                            if self.language == "spanish" or self.language == "english":
                                if self.language == "spanish":
                                    wordfrequency_num = self.WORD_FREQ_ES
                                    wordfrequency = zipf_frequency(w.text, 'es')
                                else:
                                    wordfrequency_num = self.WORD_FREQ_EN
                                    wordfrequency = zipf_frequency(w.text, 'en')
                            elif self.language == "basque":
                                if w.text in Maiztasuna.freq_list:
                                    wordfrequency_num = self.WORD_FREQ_EU
                                    wordfrequency = Maiztasuna.freq_list[w.text]
                                else:
                                    wordfrequency = None
                            if wordfrequency is not None:
                                wordfreq_list.append(float(wordfrequency))
                                num_words_in_sentences += 1
                                if w.is_lexic_word(s):
                                    if float(wordfrequency) <= wordfrequency_num:
                                        i['num_rare_words'] += 1
                                        if w.is_noun():
                                            i['num_rare_nouns'] += 1
                                            #print(w.text+":"+str(wordfrequency)+"<="+str(wordfrequency_num))
                                        elif w.is_adjective():
                                            i['num_rare_adj'] += 1
                                        elif w.is_adverb():
                                            i['num_rare_advb'] += 1
                                        elif w.is_verb(s):
                                            i['num_rare_verbs'] += 1
                                    if w.text.lower() not in self.aux_lists['different_lexic_words']:
                                        self.aux_lists['different_lexic_words'].append(w.text.lower())
                                        if float(wordfrequency) <= wordfrequency_num:
                                            i['num_dif_rare_words'] += 1
                            # words not in stopwords
                            if not w.is_stopword():
                                num_words_in_sentence_without_stopwords += 1
                                self.aux_lists['words_length_no_stopwords_list'].append(len(w.text))
                            if w.is_noun():
                                i['num_noun'] += 1
                                if w.text.lower() not in self.aux_lists['different_nouns']:
                                    self.aux_lists['different_nouns'].append(w.text.lower())
                                if w.lemma not in self.aux_lists['different_lemma_nouns'] and w.lemma is not None:
                                    self.aux_lists['different_lemma_nouns'].append(w.lemma)
                            if w.is_proper_noun():
                                i['num_proper_noun'] += 1
                            if w.is_adjective():
                                i['num_adj'] += 1
                                if w.text.lower() not in self.aux_lists['different_adjs']:
                                    self.aux_lists['different_adjs'].append(w.text.lower())
                                if w.lemma not in self.aux_lists['different_lemma_adjs'] and w.lemma is not None:
                                    self.aux_lists['different_lemma_adjs'].append(w.lemma)
                            if w.is_adverb():
                                i['num_adv'] += 1
                                if w.text.lower() not in self.aux_lists['different_advs']:
                                    self.aux_lists['different_advs'].append(w.text.lower())
                                if w.lemma not in self.aux_lists['different_lemma_advs'] and w.lemma is not None:
                                    self.aux_lists['different_lemma_advs'].append(w.lemma)
                            if w.is_verb(s):
                                i['num_verb'] += 1
                                if w.text.lower() not in self.aux_lists['different_verbs']:
                                    self.aux_lists['different_verbs'].append(w.text.lower())
                                if w.lemma not in self.aux_lists['different_lemma_verbs'] and w.lemma is not None:
                                    self.aux_lists['different_lemma_verbs'].append(w.lemma)
                                if w.is_passive():
                                    i['num_pass'] += 1
                                    if w.is_agentless(s):
                                        i['num_agentless'] += 1
                                if w.is_past():
                                    i['num_past'] += 1
                                    if w.is_irregular():
                                        i['num_past_irregular'] += 1
                                if w.is_present():
                                    i['num_pres'] += 1
                                if w.is_future(s):
                                    i['num_future'] += 1
                                if w.is_indicative():
                                    i['num_indic'] += 1
                                if w.is_gerund():
                                    i['num_ger'] += 1
                                if w.is_infinitive():
                                    i['num_inf'] += 1
                                if w.is_imperative():
                                    i['num_impera'] += 1
                            # prueba pron. pers.
                            if w.is_personal_pronoun():
                                i['num_personal_pronouns'] += 1
                            if w.is_first_person_pronoun(self.language):
                                i['num_first_pers_pron'] += 1
                            if w.is_first_personal_pronoun_sing(self.language):
                                i['num_first_pers_sing_pron'] += 1
                            if w.is_third_personal_pronoun(self.language):
                                i['num_third_pers_pron'] += 1
                            # prueba pron. pers.
                            if w.is_negative(self.language):
                                i['num_neg'] += 1
                            if w.text.lower() not in self.words_freq:
                                self.words_freq[w.text.lower()] = 1
                            else:
                                self.words_freq[w.text.lower()] = self.words_freq.get(w.text.lower()) + 1
                            if w.is_subordinate():
                                i['num_subord'] += 1
                                # Numero de sentencias subordinadas relativas
                                if w.is_subordinate_relative():
                                    i['num_rel_subord'] += 1
                            if w.is_proposition():
                                i['prop'] += 1
                            if self.language != "basque":
                                if w.has_more_than_three_syllables(self.language):
                                    i['num_words_more_3_syl'] += 1
                            if (w.is_lexic_word(s)):
                                i['num_lexic_words'] += 1
                                if wn.synsets(w.text, lang=self.wn_lang):
                                    if w.is_noun():
                                        self.aux_lists['noun_abstraction_list'].append(
                                            self.get_abstraction_level(w.text, 'n', self.wn_lang))
                                        self.aux_lists['noun_verb_abstraction_list'].append(
                                            self.get_abstraction_level(w.text, 'n', self.wn_lang))
                                    elif w.is_verb(s):
                                        self.aux_lists['verb_abstraction_list'].append(
                                            self.get_abstraction_level(w.text, 'v', self.wn_lang))
                                        self.aux_lists['noun_verb_abstraction_list'].append(
                                            self.get_abstraction_level(w.text, 'v', self.wn_lang))
                                    self.aux_lists['ambiguity_content_words_list'].append(
                                        self.get_ambiguity_level(w.text, w.upos, self.wn_lang))
                            if w.text.lower() not in self.aux_lists['different_forms']:
                                self.aux_lists['different_forms'].append(w.text.lower())
                            if w.lemma not in self.aux_lists['different_lemmas'] and w.lemma is not None:
                                self.aux_lists['different_lemmas'].append(w.text.lower())
                            self.aux_lists['words_length_list'].append(len(w.text))
                            if w.lemma is not None:
                                self.aux_lists['lemmas_length_list'].append(len(w.lemma))
                        if w.text.lower() in Oxford.a1:
                            if w.upos in Oxford.a1[w.text.lower()]:
                                i['num_a1_words'] += 1
                        elif w.text.lower() in Oxford.a2:
                            if w.upos in Oxford.a2[w.text.lower()]:
                                i['num_a2_words'] += 1
                        elif w.text.lower() in Oxford.b1:
                            if w.upos in Oxford.b1[w.text.lower()]:
                                i['num_b1_words'] += 1
                        elif w.text.lower() in Oxford.b2:
                            if w.upos in Oxford.b2[w.text.lower()]:
                                i['num_b2_words'] += 1
                        elif w.text.lower() in Oxford.c1:
                            if w.upos in Oxford.c1[w.text.lower()]:
                                i['num_c1_words'] += 1
                        elif w.is_lexic_word(s):
                            i['num_content_words_not_a1_c1_words'] += 1
                if len(wordfreq_list) > 0:
                    min_wordfreq_list.append(min(wordfreq_list))
                else:
                    min_wordfreq_list.append(0)

                i['num_total_prop'] = i['num_total_prop'] + i['prop']
                self.aux_lists['prop_per_sentence'].append(i['prop'])
                self.aux_lists['punct_per_sentence'].append(i['num_punct_in_sentence'])
                self.aux_lists['sentences_length_mean'].append(sum_s)
                self.aux_lists['sentences_length_no_stopwords_list'].append(num_words_in_sentence_without_stopwords)
                depth_list.append(self.tree_depth(dependency_tree, int(root)))
            self.aux_lists['sentences_in_paragraph_token_list'].append(sentencesPerParag)
        try:
            i['num_decendents_noun_phrase'] = round(decendents_total / sum(num_np_list), 4)
        except ZeroDivisionError:
            i['num_decendents_noun_phrase'] = 0
        try:
            i['num_modifiers_noun_phrase'] = round(float(np.mean(modifiers_per_np)), 4)
        except ZeroDivisionError:
            i['num_modifiers_noun_phrase'] = 0
        #Obtengo las sílabas del texto segun el idioma
        self.aux_lists['syllables_list']=self.get_syllable_list(text_without_punctuation)
        i['num_different_forms'] = len(self.aux_lists['different_forms'])
        i['left_embeddedness'] = round(float(np.mean(self.aux_lists['left_embeddedness'])), 4)
        i['min_wf_per_sentence'] = round(float(np.mean(min_wordfreq_list)), 4)
        self.calculate_honore()
        self.calculate_maas()
        self.calculate_phrases(num_vp_list, num_np_list)
        self.calculate_mean_depth_per_sentence(depth_list)
        self.calculate_mtld()
        self.calculate_readability()
        self.calculate_connectives()
        if similarity:
            self.calculate_similarity_adjacent_sentences()
            self.calculate_similarity_pairs_sentences()
            self.calculate_similarity_adjacent_paragraphs()

    def avg_feature_vector(self, sentence, model, num_features, index2word_set):
        words = sentence.split()
        n_words = 0
        feature_vec = np.zeros((num_features,), dtype='float32')
        for word in words:
            if word in index2word_set:
                n_words += 1
                feature_vec = np.add(feature_vec, model[word])
        if n_words > 0:
            feature_vec = np.divide(feature_vec, n_words)
        return feature_vec

    def calculate_similarity_adjacent_sentences(self):
        i = self.indicators
        adjacent_similarity_list = []

        sentences = self.aux_lists['sentences_in_text_token_list']

        for x, y in zip(range(0, len(sentences) - 1), range(1, len(sentences))):
            sim = self.calculate_similarity(sentences[x], sentences[y])
            adjacent_similarity_list.append(sim)

        if len(adjacent_similarity_list) > 0:
            i['similarity_adjacent_mean'] = round(float(np.mean(adjacent_similarity_list)), 4)
            i['similarity_adjacent_std'] = round(float(np.std(adjacent_similarity_list)), 4)

    def calculate_similarity_pairs_sentences(self):
        i = self.indicators
        pairs_similarity_list = []

        sentences = self.aux_lists['sentences_in_text_token_list']

        for s1 in sentences:
            for s2 in sentences:
                if s1.text != s2.text:
                    sim = self.calculate_similarity(s1, s2)
                    pairs_similarity_list.append(sim)

        if len(pairs_similarity_list) > 0:
            i['similarity_pairs_par_mean'] = round(float(np.mean(pairs_similarity_list)), 4)
            i['similarity_pairs_par_std'] = round(float(np.std(pairs_similarity_list)), 4)

    def calculate_similarity_pairs_paragraphs(self, p1, p2, pairs_similarity_list):
        pairs_similarity_list_mean = []
        for x in p1:
            for y in p2:
                sim = self.calculate_similarity(x, y)
                pairs_similarity_list_mean.append(sim)

        pairs_similarity_list.append(round(float(np.mean(pairs_similarity_list_mean)), 4))
        return pairs_similarity_list

    def calculate_similarity_adjacent_paragraphs(self):
        i = self.indicators
        pairs_similarity_list = []

        if len(self.aux_lists['sentences_in_paragraph_token_list']) > 1:
            for x, y in zip(range(0, len(self.aux_lists['sentences_in_paragraph_token_list']) - 1),
                            range(1, len(self.aux_lists['sentences_in_paragraph_token_list']))):
                pairs_similarity_list = self.calculate_similarity_pairs_paragraphs(
                    self.aux_lists['sentences_in_paragraph_token_list'][x],
                    self.aux_lists['sentences_in_paragraph_token_list'][y], pairs_similarity_list)

        if len(pairs_similarity_list) > 0:
            i['similarity_adjacent_par_mean'] = round(float(np.mean(pairs_similarity_list)), 4)
            i['similarity_adjacent_par_std'] = round(float(np.std(pairs_similarity_list)), 4)

    def calculate_similarity(self, s1, s2):
        s1_afv = self.avg_feature_vector(s1.text, model=self.model,
                                         num_features=self.num_features,
                                         index2word_set=self.index2word_set)
        s2_afv = self.avg_feature_vector(s2.text, model=self.model,
                                         num_features=self.num_features,
                                         index2word_set=self.index2word_set)
        sim = 1 - spatial.distance.cosine(s1_afv, s2_afv)
        return sim

    # List of syllables of each word. This will be used to calculate mean/std dev of syllables.
    def get_syllable_list(self, text_without_punctuation):
        if self.language=="basque":
            # #accedemos a foma
            # command_01 = "foma"
            # os.system(command_01)
            #
            # #utilizamos el script silabaEus que contendra las reglas
            # command_02 = "source silabaEus.script"
            # os.system(command_02)
            # Write all the information in the file
            # genera CADENAS aleatorias
            # import uuid
            #convertir a word list en word.text list
            sequence = []
            for word in text_without_punctuation:
                sequence.append(word.text)
            texto = '\t'.join(sequence)
            #longitud = len(text_without_punctuation)
            #print(longitud)
            id = uuid.uuid4()
            #print(id)
            silaba_name = str(id)
            silaba_name = silaba_name + "_silaba.txt"
            # Creamos un fichero con las palabras divididas en silabas por puntos
            with open(silaba_name, "w", encoding="utf-8") as f:
                command = "echo " + texto + " | flookup -ib data/eu/syllablesplitter/silabaEus.fst"
                # print(command)
                subprocess.run(command, shell=True, stdout=f)
            with open(silaba_name, mode="r", encoding="utf-8") as f:
                contenido = f.readlines()
                values = contenido[0].split("\t")
                # print(values[0])
                # print(values[1])
                cadena_palabras_con_puntos = values[1].split(" ")
                num_sil = []
                for palabra_con_puntos in cadena_palabras_con_puntos:
                    num_sil.append(len(palabra_con_puntos.split('.')))
                # print(num_sil)
            os.system("rm " + str(silaba_name))
            return num_sil
        if self.language == "english" or self.language == "spanish":
            num_sil = []
            for word in text_without_punctuation:
                num_sil.append(word.allnum_syllables(self.language))
            return num_sil

    def calculate_all_means(self):
        i = self.indicators
        i['sentences_per_paragraph_mean'] = round(float(np.mean(self.aux_lists['sentences_per_paragraph'])), 4)
        i['sentences_length_mean'] = round(float(np.mean(self.aux_lists['sentences_length_mean'])), 4)
        i['words_length_mean'] = round(float(np.mean(self.aux_lists['words_length_list'])), 4)
        i['lemmas_length_mean'] = round(float(np.mean(self.aux_lists['lemmas_length_list'])), 4)
        i['num_syllables_words_mean'] = round(float(np.mean(self.aux_lists['syllables_list'])), 4)
        i['mean_propositions_per_sentence'] = round(float(np.mean(self.aux_lists['prop_per_sentence'])), 4)
        i['num_punct_marks_per_sentence'] = round(float(np.mean(self.aux_lists['punct_per_sentence'])), 4)
        i['polysemic_index'] = round(float(np.mean(self.aux_lists['ambiguity_content_words_list'])), 4)
        i['hypernymy_index'] = round(float(np.mean(self.aux_lists['noun_verb_abstraction_list'])), 4)
        i['hypernymy_verbs_index'] = round(float(np.mean(self.aux_lists['verb_abstraction_list'])), 4)
        i['hypernymy_nouns_index'] = round(float(np.mean(self.aux_lists['noun_abstraction_list'])), 4)
        i['num_pass_mean'] = round((i['num_pass']) / i['num_words'], 4)
        i['num_past_irregular_mean'] = round(((i['num_past_irregular']) / i['num_past']), 4) if i['num_past'] != 0 else 0
        i['sentences_length_no_stopwords_mean'] = round(
            float(np.mean(self.aux_lists['sentences_length_no_stopwords_list'])), 4)
        i['words_length_no_stopwords_mean'] = round(float(np.mean(self.aux_lists['words_length_no_stopwords_list'])), 4)
        i['mean_rare'] = round(((100 * i['num_rare_words']) / i['num_lexic_words']), 4)
        i['mean_distinct_rare'] = round(
            (100 * i['num_dif_rare_words']) / len(self.aux_lists['different_lexic_words']), 4)

    def calculate_all_std_deviations(self):
        i = self.indicators
        i['sentences_per_paragraph_std'] = round(float(np.std(self.aux_lists['sentences_per_paragraph'])), 4)
        i['sentences_length_std'] = round(float(np.std(self.aux_lists['sentences_length_mean'])), 4)
        i['words_length_std'] = round(float(np.std(self.aux_lists['words_length_list'])), 4)
        i['lemmas_length_std'] = round(float(np.std(self.aux_lists['lemmas_length_list'])), 4)
        i['num_syllables_words_std'] = round(float(np.std(self.aux_lists['syllables_list'])), 4)
        i['sentences_length_no_stopwords_std'] = round(
            float(np.std(self.aux_lists['sentences_length_no_stopwords_list'])), 4)
        i['words_length_no_stopwords_std'] = round(float(np.std(self.aux_lists['words_length_no_stopwords_list'])), 4)

    @staticmethod
    def get_incidence(indicador, num_words):
        return round(((1000 * indicador) / num_words), 4)

    def calculate_all_incidence(self):
        i = self.indicators
        n = i['num_words']
        i['num_sentences_incidence'] = self.get_incidence(i['num_sentences'], n)
        i['num_paragraphs_incidence'] = self.get_incidence(i['num_paragraphs'], n)
        i['num_impera_incidence'] = self.get_incidence(i['num_impera'], n)
        i['num_personal_pronouns_incidence'] = self.get_incidence(i['num_personal_pronouns'], n)
        i['num_first_pers_pron_incidence'] = self.get_incidence(i['num_first_pers_pron'], n)
        i['num_first_pers_sing_pron_incidence'] = self.get_incidence(i['num_first_pers_sing_pron'], n)
        i['num_third_pers_pron_incidence'] = self.get_incidence(i['num_third_pers_pron'], n)
        i['gerund_density_incidence'] = self.get_incidence(i['num_ger'], n)
        i['infinitive_density_incidence'] = self.get_incidence(i['num_inf'], n)
        i['num_subord_incidence'] = self.get_incidence(i['num_subord'], n)
        i['num_rel_subord_incidence'] = self.get_incidence(i['num_rel_subord'], n)
        i['num_past_incidence'] = self.get_incidence(i['num_past'], n)
        i['num_pres_incidence'] = self.get_incidence(i['num_pres'], n)
        i['num_future_incidence'] = self.get_incidence(i['num_future'], n)
        i['num_indic_incidence'] = self.get_incidence(i['num_indic'], n)
        i['num_verb_incidence'] = self.get_incidence(i['num_verb'], n)
        i['num_noun_incidence'] = self.get_incidence(i['num_noun'], n)
        i['num_proper_noun_incidence'] = self.get_incidence(i['num_proper_noun'], n)
        i['num_adj_incidence'] = self.get_incidence(i['num_adj'], n)
        i['num_adv_incidence'] = self.get_incidence(i['num_adv'], n)
        i['num_pass_incidence'] = self.get_incidence(i['num_pass'], n)
        i['num_past_irregular_incidence'] = self.get_incidence(i['num_past_irregular'], n)
        i['agentless_passive_density_incidence'] = self.get_incidence(i['num_agentless'], n)
        i['num_lexic_words_incidence'] = self.get_incidence(i['num_lexic_words'], n)
        i['all_connectives_incidence'] = self.get_incidence(i['all_connectives'], n)
        i['causal_connectives_incidence'] = self.get_incidence(i['causal_connectives'], n)
        i['logical_connectives_incidence'] = self.get_incidence(i['logical_connectives'], n)
        i['adversative_connectives_incidence'] = self.get_incidence(i['adversative_connectives'], n)
        i['temporal_connectives_incidence'] = self.get_incidence(i['temporal_connectives'], n)
        i['conditional_connectives_incidence'] = self.get_incidence(i['conditional_connectives'], n)
        i['num_rare_nouns_incidence'] = self.get_incidence(i['num_rare_nouns'], n)
        i['num_rare_adj_incidence'] = self.get_incidence(i['num_rare_adj'], n)
        i['num_rare_verbs_incidence'] = self.get_incidence(i['num_rare_verbs'], n)
        i['num_rare_advb_incidence'] = self.get_incidence(i['num_rare_advb'], n)
        i['num_rare_words_incidence'] = self.get_incidence(i['num_rare_words'], n)
        i['num_dif_rare_words_incidence'] = self.get_incidence(i['num_dif_rare_words'], n)
        i['mean_rare_incidence'] = self.get_incidence(i['mean_rare'], n)
        i['mean_distinct_rare_incidence'] = self.get_incidence(i['mean_distinct_rare'], n)
        i['num_a1_words_incidence'] = self.get_incidence(i['num_a1_words'], n)
        i['num_a2_words_incidence'] = self.get_incidence(i['num_a2_words'], n)
        i['num_b1_words_incidence'] = self.get_incidence(i['num_b1_words'], n)
        i['num_b2_words_incidence'] = self.get_incidence(i['num_b2_words'], n)
        i['num_c1_words_incidence'] = self.get_incidence(i['num_c1_words'], n)
        i['num_content_words_not_a1_c1_words_incidence'] = self.get_incidence(i['num_content_words_not_a1_c1_words'], n)

    def calculate_density(self):
        i = self.indicators
        i['lexical_density'] = round(i['num_lexic_words'] / i['num_words'], 4)
        i['noun_density'] = round(i['num_noun'] / i['num_words'], 4)
        i['verb_density'] = round(i['num_verb'] / i['num_words'], 4)
        i['adj_density'] = round(i['num_adj'] / i['num_words'], 4)
        i['adv_density'] = round(i['num_adv'] / i['num_words'], 4)
        i['negation_density_incidence'] = self.get_incidence(i['num_neg'], i['num_words'])
        self.calculate_all_ttr()
        self.calculate_all_lemma_ttr()
        self.calculate_ratio_proper_nouns_per_nouns()

    def calculate_phrases(self, num_vp_list, num_np_list):
        i = self.indicators
        i['mean_vp_per_sentence'] = round(float(np.mean(num_vp_list)), 4)
        i['mean_np_per_sentence'] = round(float(np.mean(num_np_list)), 4)
        i['noun_phrase_density_incidence'] = self.get_incidence(sum(num_np_list), i['num_words'])
        i['verb_phrase_density_incidence'] = self.get_incidence(sum(num_vp_list), i['num_words'])


class Paragraph:

    def __init__(self):
        self._sentence_list = []
        self.text = None

    @property
    def sentence_list(self):
        """ Access list of sentences for this document. """
        return self._sentence_list

    @sentence_list.setter
    def sentence_list(self, value):
        """ Set the list of tokens for this document. """
        self.sentence_list = value


class Sentence:

    def __init__(self):
        self._word_list = []
        self.text = None

    @property
    def word_list(self):
        """ Access list of words for this sentence. """
        return self._word_list

    @word_list.setter
    def word_list(self, value):
        """ Set the list of words for this sentence. """
        self._word_list = value

    def calculate_left_embeddedness(self):
        verb_index = 0
        main_verb_found = False
        left_embeddedness = 0
        num_words = 0
        for word in self.word_list:
            if not len(word.text) == 1 or word.text.isalpha():
                if not main_verb_found and word.governor < len(self.word_list):
                    if word.is_verb(self):
                        verb_index += 1
                        if (word.upos == 'VERB' and word.dependency_relation == 'root') or (
                                word.upos == 'AUX' and self.word_list[
                            word.governor].dependency_relation == 'root'
                                and self.word_list[word.governor].upos == 'VERB'):
                            main_verb_found = True
                            left_embeddedness = num_words
                        if verb_index == 1:
                            left_embeddedness = num_words
                num_words += 1
        return left_embeddedness

    def count_np_in_sentence(self):
        list_np_indexes = []
        for word in self.word_list:
            list_np_indexes = word.is_np(list_np_indexes)
        return list_np_indexes

    def count_vp_in_sentence(self):
        num_vp = 0
        for entry in self.word_list:
            if entry.is_verb(self):
                num_vp += 1
        return num_vp

    def count_modifiers(self, list_np_indexes):
        num_modifiers_per_np = []
        for index in list_np_indexes:
            num_modifiers = 0
            for entry in self.word_list:
                if int(entry.governor) == int(index) and entry.has_modifier():
                    num_modifiers += 1
            num_modifiers_per_np.append(num_modifiers)
        return num_modifiers_per_np

    def count_decendents(self, list_np_indexes):
        num_modifiers = 0
        if len(list_np_indexes) == 0:
            return num_modifiers
        else:
            new_list_indexes = []
            for entry in self.word_list:
                if entry.governor in list_np_indexes and entry.has_modifier():
                    new_list_indexes.append(entry.index)
                    num_modifiers += 1
            return num_modifiers + self.count_decendents(new_list_indexes)

    # Metodo que calcula el numero de palabras de contenido en una frase. Counts number of content words in a sentence.
    def count_content_words_in(self):
        num_words = 0
        for entry in self.word_list:
            if entry.is_verb(self) or entry.is_noun() or entry.is_adjective() or entry.is_adverb():
                num_words += 1
        return num_words

    def print(self):
        for words in self.word_list:
            print(words.text)


class Word:
    def __init__(self):
        self._index = None
        self._text = None
        self._lemma = None
        self._upos = None
        self._xpos = None
        self._feats = None
        self._governor = None
        self._dependency_relation = None

    @property
    def dependency_relation(self):
        """ Access dependency relation of this word. Example: 'nmod'"""
        return self._dependency_relation

    @dependency_relation.setter
    def dependency_relation(self, value):
        """ Set the word's dependency relation value. Example: 'nmod'"""
        self._dependency_relation = value

    @property
    def lemma(self):
        """ Access lemma of this word. """
        return self._lemma

    @lemma.setter
    def lemma(self, value):
        """ Set the word's lemma value. """
        self._lemma = value

    @property
    def governor(self):
        """ Access governor of this word. """
        return self._governor

    @governor.setter
    def governor(self, value):
        """ Set the word's governor value. """
        self._governor = value

    @property
    def pos(self):
        """ Access (treebank-specific) part-of-speech of this word. Example: 'NNP'"""
        return self._xpos

    @pos.setter
    def pos(self, value):
        """ Set the word's (treebank-specific) part-of-speech value. Example: 'NNP'"""
        self._xpos = value

    @property
    def text(self):
        """ Access text of this word. Example: 'The'"""
        return self._text

    @text.setter
    def text(self, value):
        """ Set the word's text value. Example: 'The'"""
        self._text = value

    @property
    def xpos(self):
        """ Access treebank-specific part-of-speech of this word. Example: 'NNP'"""
        return self._xpos

    @xpos.setter
    def xpos(self, value):
        """ Set the word's treebank-specific part-of-speech value. Example: 'NNP'"""
        self._xpos = value

    @property
    def upos(self):
        """ Access universal part-of-speech of this word. Example: 'DET'"""
        return self._upos

    @upos.setter
    def upos(self, value):
        """ Set the word's universal part-of-speech value. Example: 'DET'"""
        self._upos = value

    @property
    def feats(self):
        """ Access morphological features of this word. Example: 'Gender=Fem'"""
        return self._feats

    @feats.setter
    def feats(self, value):
        """ Set this word's morphological features. Example: 'Gender=Fem'"""
        self._feats = value

    @property
    def parent_token(self):
        """ Access the parent token of this word. """
        return self._parent_token

    @parent_token.setter
    def parent_token(self, value):
        """ Set this word's parent token. """
        self._parent_token = value

    @property
    def index(self):
        """ Access index of this word. """
        return self._index

    @index.setter
    def index(self, value):
        """ Set the word's index value. """
        self._index = value

    def has_modifier(self):
        # nominal head may be associated with different types of modifiers and function words
        return True if self.dependency_relation in ['nmod', 'nmod:poss', 'appos', 'amod', 'nummod', 'acl', 'acl:relcl',
                                                    'det', 'clf',
                                                    'case'] else False

    def is_personal_pronoun(self):
        atributos = self.feats.split('|')
        if "PronType=Prs" in atributos:
            return True
        else:
            return False

    def is_first_person_pronoun(self, language):
        atributos = self.feats.split('|')
        if 'PronType=Prs' in atributos and 'Person=1' in atributos:
            return True
        else:
            return False

    def is_third_personal_pronoun(self, language):
        atributos = self.feats.split('|')
        if 'PronType=Prs' in atributos and 'Person=3' in atributos:
            return True
        else:
            return False

    def is_first_personal_pronoun_sing(self, language):
        atributos = self.feats.split('|')
        if 'PronType=Prs' in atributos and 'Person=1' in atributos and 'Number=Sing' in atributos:
            return True
        else:
            return False

    def num_syllables(self):
        list = []
        max = 0
        txt = self.text.lower()
        for x in Pronouncing.prondict[txt]:
            tmp_list = []
            tmp_max = 0
            for y in x:
                if y[-1].isdigit():
                    tmp_max += 1
                    tmp_list.append(y)
            list.append(tmp_list)
            if tmp_max > max:
                max = tmp_max
        return max

    def syllables_en(self):
        """
                Calculate syllables of a word using a less accurate algorithm.
                Parse through the sentence, using common syllabic identifiers to count
                syllables.

                ADAPTED FROM:
                [http://stackoverflow.com/questions/14541303/count-the-number-of-syllables-in-a-word]
                """
        # initialize count
        count = 0
        # vowel list
        vowels = 'aeiouy'
        # take out punctuation
        word = self.text.lower()  # word.lower().strip(".:;?!")
        # various signifiers of syllabic up or down count
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') or word.endswith('a'):
            count += 1
        if count == 0:
            count += 1
        if "ooo" in word or "mm" in word:
            count = 1
        if word == 'll':
            count = 0
        if (word.startswith('x') and len(word) >= 2) and word[1].isdigit():
            count = 0
        if word == 'lmfao':
            count = 5
        if len(word) < 2 and word not in ['a', 'i', 'y', 'o']:
            count = 0
        return count

    def syllables_es(self):
        chars = char_line(re.sub(r'\W+', '', self.text))
        return len(self.syllablesplit(chars))

    def syllablesplit(self, chars):
        rules = [('VV', 1), ('cccc', 2), ('xcc', 1), ('ccx', 2), ('csc', 2), ('xc', 1), ('cc', 1), ('vcc', 2),
                 ('Vcc', 2), ('sc', 1), ('cs', 1), ('Vc', 1), ('vc', 1), ('Vs', 1), ('vs', 1)]
        for split_rule, where in rules:
            first, second = chars.split_by(split_rule, where)
            if second:
                if first.type_line in set(['c', 's', 'x', 'cs']) or second.type_line in set(['c', 's', 'x', 'cs']):
                    # print 'skip1', first.word, second.word, split_rule, chars.type_line
                    continue
                if first.type_line[-1] == 'c' and second.word[0] in set(['l', 'r']):
                    continue
                if first.word[-1] == 'l' and second.word[-1] == 'l':
                    continue
                if first.word[-1] == 'r' and second.word[-1] == 'r':
                    continue
                if first.word[-1] == 'c' and second.word[-1] == 'h':
                    continue
                return self.syllablesplit(first) + self.syllablesplit(second)
        return [chars]

    def allnum_syllables(self,lang):
        if lang == "english":
            try:
                return self.num_syllables()
            except KeyError:
                # if word not found in cmudict
                return self.syllables_en()
        if lang == "spanish":
            return self.syllables_es()

    def is_lexic_word(self, sequence):
        return self.is_verb(sequence) or self.upos == 'NOUN' or self.upos == 'ADJ' or self.upos == 'ADV'

    def is_verb(self, frase):
        return self.upos == 'VERB' or (self.upos == 'AUX' and frase.word_list[self.governor - 1].upos != 'VERB')

    def is_future(self, frase):
        return self.upos == 'AUX' and self.lemma in ['will', 'shall'] and frase.word_list[
            int(self.governor) - 1].xpos == 'VB'

    def is_past(self):
        atributos = self.feats.split('|')
        if 'Tense=Past' in atributos:
            return True
        else:
            return False

    def is_present(self):
        atributos = self.feats.split('|')
        if "Tense=Pres" in atributos:
            return True
        else:
            return False

    def is_indicative(self):
        atributos = self.feats.split('|')
        if "Mood=Ind" in atributos:
            return True
        else:
            return False

    def is_np(self, list_np_indexes):
        if self.upos == 'NOUN' or self.upos == 'PRON' or self.upos == 'PROPN':
            if self.dependency_relation in ['fixed', 'flat', 'compound']:
                if self.governor not in list_np_indexes:
                    list_np_indexes.append(self.governor)
            else:
                if self.index not in list_np_indexes:
                    ind = int(self.index)
                    list_np_indexes.append(ind)
        return list_np_indexes

    def is_gerund(self):
        atributos = self.feats.split('|')
        if 'VerbForm=Ger' in atributos:
            return True
        else:
            return False

    def is_infinitive(self):
        atributos = self.feats.split('|')
        if 'VerbForm=Inf' in atributos:
            return True
        else:
            return False

    def is_imperative(self):
        atributos = self.feats.split('|')
        if 'Mood=Imp' in atributos:
            return True
        else:
            return False

    def is_proposition(self):
        if self.dependency_relation == 'conj' or self.dependency_relation == 'csubj' or self.dependency_relation == 'csubj:pass' or \
                self.dependency_relation == 'ccomp' or self.dependency_relation == 'xcomp' or self.dependency_relation == 'advcl' or self.dependency_relation == 'acl' or self.dependency_relation == 'acl:relcl':
            return True
        else:
            return False

    def is_subordinate(self):
        subordinadas_labels = ['csubj', 'csubj:pass', 'ccomp', 'xcomp',
                               'advcl', 'acl', 'acl:relcl']
        return True if self.dependency_relation in subordinadas_labels else False

    def is_subordinate_relative(self):
        subordinate_relative_labels = ['acl:relcl']

        return True if self.dependency_relation in subordinate_relative_labels else False

    def is_stopword(self):
        return True if self.text.lower() in Stopwords.stop_words else False

    def is_punctuation(self):
        # Punctuation marks are non-alphabetical characters and character groups used in many languages to delimit linguistic units in printed text.
        if self.upos == 'PUNCT':
            return True
        else:
            return False

    def __repr__(self):
        features = ['index', 'text', 'lemma', 'upos', 'xpos', 'feats', 'governor', 'dependency_relation']
        feature_str = ";".join(["{}={}".format(k, getattr(self, k)) for k in features if getattr(self, k) is not None])

        return f"<{self.__class__.__name__} {feature_str}>"

    def is_num(self):
        if self.upos == 'NUM':
            return True
        else:
            return False

    def is_noun(self):
        if self.upos == 'NOUN':
            return True
        else:
            return False

    def is_proper_noun(self):
        if self.upos == "PROPN":
            return True
        else:
            return False

    def is_adjective(self):
        if self.upos == 'ADJ':
            return True
        else:
            return False

    def is_adverb(self):
        if self.upos == 'ADV':
            return True
        else:
            return False

    def is_negative(self, lang):
        if lang == "english":
            if self.lemma == 'not':
                return True
            else:
                return False
        else:
            atributos = self.feats.split('|')
            if 'Polarity=Neg' in atributos:
                return True
            else:
                return False

    def is_irregular(self):
        return True if self.lemma in Irregularverbs.irregular_verbs else False

    def has_more_than_three_syllables(self,lang):
        return True if self.allnum_syllables(lang) > 3 else False

    def is_passive(self):
        atributos = self.feats.split('|')
        return True if 'Voice=Pass' in atributos else False

    def is_agentless(self, frase):
        # Si el siguiente indice esta dentro del rango de la lista
        if int(self.index) < len(frase.word_list):
            siguiente = frase.word_list[int(self.index) + 1].text.lower()
            if siguiente == 'by' or siguiente == 'por':
                return False
            else:
                return True


class Oxford():
    a1 = defaultdict(dict)
    a2 = defaultdict(dict)
    b1 = defaultdict(dict)
    b2 = defaultdict(dict)
    c1 = defaultdict(dict)

    def load(self):
        f = open('data/en/Vocabularylevel/OxfordWordListByLevel.txt', 'r', encoding='utf-8')
        lineas = f.readlines()
        aux = Oxford.a1
        for linea in lineas:
            if linea.startswith("//A1"):
                aux = Oxford.a1
            elif linea.startswith("//A2"):
                aux = Oxford.a2
            elif linea.startswith("//B1"):
                aux = Oxford.b1
            elif linea.startswith("//B2"):
                aux = Oxford.b2
            elif linea.startswith("//C1"):
                aux = Oxford.c1
            else:
                aux[linea.split()[0]] = linea.split()[1].rstrip('\n')
        f.close()


class Connectives():
    connectives = []
    lang = ""
    # en
    logical = []
    adversative = []
    # both
    temporal = []
    causal = []
    conditional = []
    def __init__(self, language):
        Connectives.lang = language
    def load(self):
        if Connectives.lang == "spanish":
            f = open('data/es/Connectives/connectives.txt', 'r', encoding='utf-8')
        if Connectives.lang == "english":
            f = open('data/en/Connectives/connectives.txt', 'r', encoding='utf-8')
        if Connectives.lang == "basque":
            f = open('data/eu/Connectives/connectives.txt', 'r', encoding='utf-8')
        lineas = f.readlines()
        aux = Connectives.temporal
        for linea in lineas:
            if linea.startswith("//causal"):
                aux = Connectives.causal
            elif linea.startswith("//conditional"):
                aux = Connectives.conditional
            elif linea.startswith("//temporal"):
                aux = Connectives.temporal
            elif linea.startswith("//logical"):
                aux = Connectives.logical
            elif linea.startswith("//adversative"):
                aux = Connectives.adversative
            else:
                aux.append(linea.rstrip('\n'))
                Connectives.connectives.append(linea.rstrip('\n'))
        f.close()


class char_line():
    def __init__(self, word):
        self.word = word
        self.char_line = [(char, self.char_type(char)) for char in word]
        self.type_line = ''.join(chartype for char, chartype in self.char_line)

    def char_type(self, char):
        if char in set(['a', 'á', 'e', 'é', 'o', 'ó', 'í', 'ú']):
            return 'V'  # strong vowel
        if char in set(['i', 'u', 'ü']):
            return 'v'  # week vowel
        if char == 'x':
            return 'x'
        if char == 's':
            return 's'
        else:
            return 'c'

    def find(self, finder):
        return self.type_line.find(finder)

    def split(self, pos, where):
        return char_line(self.word[0:pos + where]), char_line(self.word[pos + where:])

    def split_by(self, finder, where):
        split_point = self.find(finder)
        if split_point != -1:
            chl1, chl2 = self.split(split_point, where)
            return chl1, chl2
        return self, False

    def __str__(self):
        return self.word

    def __repr__(self):
        return repr(self.word)


class Irregularverbs():

    irregular_verbs = []
    def __init__(self, language):
        self.lang = language

    def load(self):
        if self.lang.lower() == "spanish":
            f = open('data/es/IrregularVerbs/irregularverbs.txt', 'r', encoding='ISO-8859-1')
            lineas = f.readlines()
            for linea in lineas:
                if not linea.startswith("//"):
                    # carga el verbo en presente, dejando pasado y preterito
                    Irregularverbs.irregular_verbs.append(linea.rstrip('\n'))
            f.close()
        if self.lang.lower() == "english":
            f = open('data/en/IrregularVerbs/IrregularVerbs.txt', 'r', encoding='utf-8')
            lineas = f.readlines()
            for linea in lineas:
                if not linea.startswith("//"):
                    #carga el verbo en presente, dejando pasado y preterito
                    Irregularverbs.irregular_verbs.append(linea.split()[0])
            f.close()


class Printer:

    def __init__(self, indicators, language, similarity):
        self.indicators = indicators
        self.language = language
        self.similarity = similarity
        self.ind_sentences = {}
        # ignore list inicializados
        self.ignore_list_en_ind = []
        self.ignore_list_es_ind = []
        self.ignore_list_eu_ind = []
        self.ignore_list_counters = []
        self.similarity_list = []

    def load_ind_sentences(self):
        self.ind_sentences['num_words'] = "Number of words (total): "
        # The number of distints lower and alfabetic words
        self.ind_sentences['num_different_forms'] = "Number of distinct words (total): "
        self.ind_sentences['num_words_with_punct'] = "Number of words with punctuation (total): "
        self.ind_sentences['num_paragraphs'] = "Number of paragraphs (total): "
        self.ind_sentences['num_paragraphs_incidence'] = "Number of paragraphs (incidence per 1000 words): "
        self.ind_sentences['num_sentences'] = "Number of sentences (total): "
        self.ind_sentences['num_sentences_incidence'] = "Number of sentences (incidence per 1000 words): "
        # Numero de frases en un parrafo (media)
        self.ind_sentences['sentences_per_paragraph_mean'] = "Length of paragraphs (mean): "
        # Numero de frases en un parrafo (desv. Tipica)
        self.ind_sentences['sentences_per_paragraph_std'] = "Standard deviation of length of paragraphs: "
        self.ind_sentences['sentences_length_mean'] = "Number of words (length) in sentences (mean): "
        self.ind_sentences['sentences_length_std'] = "Number of words (length) in sentences (standard deviation): "
        self.ind_sentences['sentences_length_no_stopwords_mean'] = "Number of words (length) of sentences without " \
                                                                   "stopwords (mean): "
        self.ind_sentences['sentences_length_no_stopwords_std'] = "Number of words (length) of sentences without " \
                                                                  "stopwords (standard deviation): "
        self.ind_sentences['num_syllables_words_mean'] = "Mean number of syllables (length) in words: "
        self.ind_sentences['num_syllables_words_std'] = "Standard deviation of the mean number of syllables in words: "
        self.ind_sentences['words_length_mean'] = "Mean number of letters (length) in words: "
        self.ind_sentences['words_length_std'] = "Standard deviation of number of letters in words: "
        self.ind_sentences['words_length_no_stopwords_mean'] = "Mean number of letters (length) in words without " \
                                                               "stopwords: "
        self.ind_sentences['words_length_no_stopwords_std'] = "Standard deviation of the mean number of letter in " \
                                                              "words without stopwords: "
        self.ind_sentences['lemmas_length_mean'] = "Mean number of letters (length) in lemmas: "
        self.ind_sentences['lemmas_length_std'] = "Standard deviation of letters (length) in lemmas: "
        self.ind_sentences['lexical_density'] = "Lexical Density: "
        self.ind_sentences['noun_density'] = "Noun Density: "
        self.ind_sentences['verb_density'] = "Verb Density: "
        self.ind_sentences['adj_density'] = "Adjective Density: "
        self.ind_sentences['adv_density'] = "Adverb Density: "
        # calculate_ratio_proper_nouns_per_nouns
        self.ind_sentences[
            'ratio_proper_nouns_per_nouns'] = "Ratio of proper nouns for all nouns (proper and common nouns): "
        # Simple TTR (Type-Token Ratio)
        self.ind_sentences['simple_ttr'] = "STTR (Simple Type-Token Ratio) : "
        # Content TTR (Content Type-Token Ratio)
        self.ind_sentences['content_ttr'] = "CTTR (Content Type-Token Ratio): "
        # NTTR (Noun Type-Token Ratio)
        self.ind_sentences['nttr'] = "NTTR (Noun Type-Token Ratio): "
        # VTTR (Verb Type-Token Ratio)(incidence per 1000 words)
        self.ind_sentences['vttr'] = "VTTR (Verb Type-Token Ratio): "
        # AdjTTR (Adj Type-Token Ratio)
        self.ind_sentences['adj_ttr'] = "AdjTTR (Adj Type-Token Ratio): "
        # AdvTTR (Adv Type-Token Ratio)
        self.ind_sentences['adv_ttr'] = "AdvTTR (Adv Type-Token Ratio): "
        # Lemma Simple TTR (Type-Token Ratio)
        self.ind_sentences['lemma_ttr'] = "LSTTR (Lemma Simple Type-Token Ratio): "
        # Lemma Content TTR (Content Type-Token Ratio)
        self.ind_sentences['lemma_content_ttr'] = "LCTTR (Lemma Content Type-Token Ratio): "
        # LNTTR (Lemma Noun Type-Token Ratio)
        self.ind_sentences['lemma_nttr'] = "LNTTR (Lemma Noun Type-Token Ratio): "
        # LVTTR (Lemma Verb Type-Token Ratio)
        self.ind_sentences['lemma_vttr'] = "LVTTR (Lemma Verb Type-Token Ratio): "
        # Lemma AdjTTR (Lemma Adj Type-Token Ratio)
        self.ind_sentences['lemma_adj_ttr'] = "LAdjTTR (Lemma Adj Type-Token Ratio): "
        # Lemma AdvTTR (Lemma Adv Type-Token Ratio)
        self.ind_sentences['lemma_adv_ttr'] = "LAdvTTR (Lemma Adv Type-Token Ratio): "
        # Honore
        self.ind_sentences['honore'] = "Honore Lexical Density: "
        # Maas
        self.ind_sentences['maas'] = "Maas Lexical Density: "
        # MTLD
        self.ind_sentences['mtld'] = "Measure of Textual Lexical Diversity (MTLD): "
        # Flesch readability ease=206.835-1.015(n.º de words/nº de frases)-84.6(n.º de silabas/numero de words)
        self.ind_sentences['flesch'] = "Flesch readability ease: "
        # Flesch-Kincaid grade level =0.39 * (n.º de words/nº de frases) + 11.8 * (n.º de silabas/numero de words) – 15.59)
        self.ind_sentences['flesch_kincaid'] = "Flesch-Kincaid Grade level: "
        self.ind_sentences['dale_chall'] = "Dale-Chall readability formula: "
        self.ind_sentences['smog'] = "Simple Measure Of Gobbledygook (SMOG) grade: "
        self.ind_sentences['num_a1_words'] = "Number of A1 vocabulary in the text: "
        self.ind_sentences['num_a1_words_incidence'] = "Incidence score of A1 vocabulary  (per 1000 words): "
        self.ind_sentences['num_a2_words'] = "Number of A2 vocabulary in the text: "
        self.ind_sentences['num_a2_words_incidence'] = "Incidence score of A2 vocabulary  (per 1000 words): "
        self.ind_sentences['num_b1_words'] = "Number of B1 vocabulary in the text: "
        self.ind_sentences['num_b1_words_incidence'] = "Incidence score of B1 vocabulary  (per 1000 words): "
        self.ind_sentences['num_b2_words'] = "Number of B2 vocabulary in the text: "
        self.ind_sentences['num_b2_words_incidence'] = "Incidence score of B2 vocabulary  (per 1000 words): "
        self.ind_sentences['num_c1_words'] = "Number of C1 vocabulary in the text: "
        self.ind_sentences['num_c1_words_incidence'] = "Incidence score of C1 vocabulary  (per 1000 words): "
        self.ind_sentences['num_content_words_not_a1_c1_words'] = "Number of content words not in A1-C1 vocabulary: "
        self.ind_sentences['num_content_words_not_a1_c1_words_incidence'] = "Incidence score of content words not in " \
                                                                            "A1-C1 vocabulary (per 1000 words): "
        self.ind_sentences['num_past'] = "Number of verbs in past tense: "
        self.ind_sentences['num_past_incidence'] = "Number of verbs in past tense (incidence per 1000 words): "
        self.ind_sentences['num_pres'] = "Number of verbs in present tense: "
        self.ind_sentences['num_pres_incidence'] = "Number of verbs in present tense (incidence per 1000 words): "
        self.ind_sentences['num_future'] = "Number of verbs in future tense: "
        self.ind_sentences['num_future_incidence'] = "Number of verbs in future tense (incidence per 1000 words): "
        # Numero de verbos en modo indicativo
        self.ind_sentences['num_indic'] = "Number of verbs in indicative mood: "
        self.ind_sentences['num_indic_incidence'] = "Number of verbs in indicative mood (incidence per 1000 words): "
        # Numero de verbos en modo imperativo
        self.ind_sentences['num_impera'] = "Number of verbs in imperative mood: "
        self.ind_sentences['num_impera_incidence'] = "Number of verbs in imperative mood (incidence per 1000 words): "
        # Numero de verbos en pasado que son irregulares
        self.ind_sentences['num_past_irregular'] = "Number of irregular verbs in past tense: "
        # Numero de verbos en pasado que son irregulares (incidencia 1000 words)
        self.ind_sentences['num_past_irregular_incidence'] = "Number of irregular verbs in past tense (incidence per " \
                                                             "1000 words): "
        # Porcentaje de verbos en pasado que son irregulares sobre total de verbos en pasado
        self.ind_sentences['num_past_irregular_mean'] = "Mean of irregular verbs in past tense in relation to the " \
                                                        "number of verbs in past tense: "
        # Number of personal pronouns
        self.ind_sentences['num_personal_pronouns'] = "Number of personal pronouns: "
        # Incidence score of pronouns (per 1000 words)
        self.ind_sentences['num_personal_pronouns_incidence'] = "Incidence score of pronouns (per 1000 words): "
        # Number of pronouns in first person
        self.ind_sentences['num_first_pers_pron'] = "Number of pronouns in first person: "
        # Incidence score of pronouns in first person  (per 1000 words)
        self.ind_sentences['num_first_pers_pron_incidence'] = "Incidence score of pronouns in first person  (per 1000 " \
                                                              "words): "
        # Number of pronouns in first person singular
        self.ind_sentences['num_first_pers_sing_pron'] = "Number of pronouns in first person singular: "
        # Incidence score of pronouns in first person singular (per 1000 words)
        self.ind_sentences['num_first_pers_sing_pron_incidence'] = "Incidence score of pronouns in first person " \
                                                                   "singular (per 1000 words): "
        # Number of pronouns in third person
        self.ind_sentences['num_third_pers_pron'] = "Number of pronouns in third person: "
        # Incidence score of pronouns in third person (per 1000 words)
        self.ind_sentences['num_third_pers_pron_incidence'] = "Incidence score of pronouns in third person (per 1000 " \
                                                              "words): "
        self.ind_sentences['min_wf_per_sentence'] = "Minimum word frequency per sentence (mean): "
        self.ind_sentences['num_rare_nouns'] = "Number of rare nouns: "
        self.ind_sentences['num_rare_nouns_incidence'] = "Number of rare nouns (incidence per 1000 words): "
        self.ind_sentences['num_rare_adj'] = "Number of rare adjectives: "
        self.ind_sentences['num_rare_adj_incidence'] = "Number of rare adjectives (incidence per 1000 words): "
        self.ind_sentences['num_rare_verbs'] = "Number of rare verbs: "
        self.ind_sentences['num_rare_verbs_incidence'] = "Number of rare verbs (incidence per 1000 words): "
        self.ind_sentences['num_rare_advb'] = "Number of rare adverbs: "
        self.ind_sentences['num_rare_advb_incidence'] = "Number of rare adverbs (incidence per 1000 words): "
        self.ind_sentences['num_rare_words'] = "Number of rare content words: "
        self.ind_sentences['num_rare_words_incidence'] = "Number of rare content words (incidence per 1000 words): "
        self.ind_sentences['num_dif_rare_words'] = "Number of distinct rare content words: "
        self.ind_sentences['num_dif_rare_words_incidence'] = "Number of distinct rare content words (incidence per " \
                                                             "1000 words): "
        # The average of rare lexical words (whose word frequency value is less than 4) with respect to the total of lexical words
        self.ind_sentences['mean_rare'] = "Mean of rare lexical words: "
        # The average of distinct rare lexical words (whose word frequency value is less than 4) with respect to the total of distinct lexical words
        self.ind_sentences['mean_distinct_rare'] = "Mean of distinct rare lexical words: "
        self.ind_sentences['num_lexic_words'] = "Number of content words: "
        self.ind_sentences['num_lexic_words_incidence'] = "Number of content words (incidence per 1000 words): "
        self.ind_sentences['num_noun'] = "Number of nouns: "
        self.ind_sentences['num_noun_incidence'] = "Number of nouns (incidence per 1000 words): "
        self.ind_sentences['num_proper_noun'] = "Number of proper nouns: "
        self.ind_sentences['num_proper_noun_incidence'] = "Number of proper nouns (incidence per 1000 words): "
        self.ind_sentences['num_adj'] = "Number of adjectives: "
        self.ind_sentences['num_adj_incidence'] = "Number of adjectives (incidence per 1000 words): "
        self.ind_sentences['num_adv'] = "Number of adverbs: "
        self.ind_sentences['num_adv_incidence'] = "Number of adverbs (incidence per 1000 words): "
        self.ind_sentences['num_verb'] = "Number of verbs: "
        self.ind_sentences['num_verb_incidence'] = "Number of verbs (incidence per 1000 words): "
        # Left-Embeddedness
        self.ind_sentences['left_embeddedness'] = "Left embeddedness (Mean of number of words before the main verb) (" \
                                                  "SYNLE): "
        self.ind_sentences['num_decendents_noun_phrase'] = "Number of decendents per noun phrase (mean): "
        self.ind_sentences['num_modifiers_noun_phrase'] = "Number of modifiers per noun phrase (mean) (SYNNP): "
        self.ind_sentences['mean_depth_per_sentence'] = "Mean of the number of levels of dependency tree (Depth): "
        # Numero de sentencias subordinadas
        self.ind_sentences['num_subord'] = "Number of subordinate clauses: "
        # Numero de sentencias subordinadas (incidence per 1000 words)
        self.ind_sentences['num_subord_incidence'] = "Number of subordinate clauses (incidence per 1000 words): "
        # Numero de sentencias subordinadas relativas
        self.ind_sentences['num_rel_subord'] = "Number of relative subordinate clauses: "
        # Numero de sentencias subordinadas relativas (incidence per 1000 words)
        self.ind_sentences['num_rel_subord_incidence'] = "Number of relative subordinate clauses (incidence per 1000 " \
                                                         "words): "
        # Marcas de puntuacion por sentencia (media)
        self.ind_sentences['num_punct_marks_per_sentence'] = "Punctuation marks per sentence (mean): "
        self.ind_sentences['num_total_prop'] = "Number of propositions: "
        # Mean of the number of propositions per sentence
        self.ind_sentences['mean_propositions_per_sentence'] = "Mean of the number of propositions per sentence: "
        self.ind_sentences['mean_vp_per_sentence'] = "Mean of the number of VPs per sentence: "
        self.ind_sentences['mean_np_per_sentence'] = "Mean of the number of NPs per sentence: "
        self.ind_sentences['noun_phrase_density_incidence'] = "Noun phrase density, incidence (DRNP): "
        self.ind_sentences['verb_phrase_density_incidence'] = "Verb phrase density, incidence (DRVP): "
        # Numero de verbos en pasiva (total)
        self.ind_sentences['num_pass'] = "Number of passive voice verbs: "
        # Numero de verbos en pasiva (incidence per 1000 words)
        self.ind_sentences['num_pass_incidence'] = "Number of passive voice verbs (incidence per 1000 words): "
        # Porcentaje de verbos en pasiva
        self.ind_sentences['num_pass_mean'] = "Mean of passive voice verbs: "
        # Numero de verbos en pasiva que no tienen agente
        self.ind_sentences['num_agentless'] = "Number of agentless passive voice verbs: "
        self.ind_sentences['agentless_passive_density_incidence'] = "Agentless passive voice density, incidence (" \
                                                                    "DRPVAL): "
        self.ind_sentences['num_neg'] = "Number of negative words: "
        self.ind_sentences['negation_density_incidence'] = "Negation density, incidence (DRNEG): "
        self.ind_sentences['num_ger'] = "Number of verbs in gerund form: "
        self.ind_sentences['gerund_density_incidence'] = "Gerund density, incidence (DRGERUND): "
        self.ind_sentences['num_inf'] = "Number of verbs in infinitive form: "
        self.ind_sentences['infinitive_density_incidence'] = "Infinitive density, incidence (DRINF): "
        # Ambigüedad de una palabra (polysemy in WordNet)
        self.ind_sentences['polysemic_index'] = "Mean values of polysemy in the WordNet lexicon: "
        # Nivel de abstracción (hypernym in WordNet)
        self.ind_sentences['hypernymy_verbs_index'] = "Mean hypernym values of verbs in the WordNet lexicon: "
        self.ind_sentences['hypernymy_nouns_index'] = "Mean hypernym values of nouns in the WordNet lexicon: "
        self.ind_sentences['hypernymy_index'] = "Mean hypernym values of nouns and verbs in the WordNet lexicon: "
        # Textbase. Referential cohesion
        self.ind_sentences['noun_overlap_adjacent'] = "Noun overlap, adjacent sentences, binary, mean (CRFNOl): "
        self.ind_sentences['noun_overlap_all'] = "Noun overlap, all of the sentences in a paragraph or text, binary, " \
                                                 "mean (CRFNOa): "
        self.ind_sentences['argument_overlap_adjacent'] = "Argument overlap, adjacent sentences, binary, mean (" \
                                                          "CRFAOl): "
        self.ind_sentences['argument_overlap_all'] = "Argument overlap, all of the sentences in a paragraph or text, " \
                                                     "binary, mean (CRFAOa): "
        self.ind_sentences['stem_overlap_adjacent'] = "Stem overlap, adjacent sentences, binary, mean (CRFSOl): "
        self.ind_sentences['stem_overlap_all'] = "Stem overlap, all of the sentences in a paragraph or text, binary, " \
                                                 "mean (CRFSOa): "
        self.ind_sentences['content_overlap_adjacent_mean'] = "Content word overlap, adjacent sentences, " \
                                                              "proportional, mean (CRFCWO1): "
        self.ind_sentences['content_overlap_adjacent_std'] = "Content word overlap, adjacent sentences, proportional, " \
                                                             "standard deviation (CRFCWO1d): "
        self.ind_sentences['content_overlap_all_mean'] = "Content word overlap, all of the sentences in a paragraph " \
                                                         "or text, proportional, mean (CRFCWOa): "
        self.ind_sentences['content_overlap_all_std'] = "Content word overlap, all of the sentences in a paragraph or " \
                                                        "text, proportional, standard deviation (CRFCWOad): "
        # Connectives
        self.ind_sentences['all_connectives'] = "Number of connectives: "
        self.ind_sentences['all_connectives_incidence'] = "Number of connectives (incidence per 1000 words): "
        self.ind_sentences['causal_connectives'] = "Causal connectives: "
        self.ind_sentences['causal_connectives_incidence'] = "Causal connectives (incidence per 1000 words): "
        self.ind_sentences['temporal_connectives'] = "Temporal connectives:  "
        self.ind_sentences['temporal_connectives_incidence'] = "Temporal connectives (incidence per 1000 words):  "
        self.ind_sentences['conditional_connectives'] = "Conditional connectives: "
        self.ind_sentences['conditional_connectives_incidence'] = "Conditional connectives (incidence per 1000 words): "
        self.ind_sentences['logical_connectives'] = "Logical connectives:  "
        self.ind_sentences['logical_connectives_incidence'] = "Logical connectives (incidence per 1000 words):  "
        self.ind_sentences['adversative_connectives'] = "Adversative/contrastive connectives: "
        self.ind_sentences[
            'adversative_connectives_incidence'] = "Adversative/contrastive connectives (incidence per 1000 words): "
        self.ind_sentences['similarity_adjacent_mean'] = "Semantic Similarity between adjacent sentences (mean): "
        self.ind_sentences[
            'similarity_pairs_par_mean'] = "Semantic Similarity between all possible pairs of sentences in a " \
                                           "paragraph (mean): "
        self.ind_sentences['similarity_adjacent_par_mean'] = "Semantic Similarity between adjacent paragraphs (mean): "
        self.ind_sentences[
            'similarity_adjacent_std'] = "Semantic Similarity between adjacent sentences (standard deviation): "
        self.ind_sentences[
            'similarity_pairs_par_std'] = "Semantic Similarity between all possible pairs of sentences in a paragraph " \
                                          "(standard deviation): "
        self.ind_sentences[
            'similarity_adjacent_par_std'] = "Semantic Similarity between adjacent paragraphs (standard deviation): "

        self.load_ignore_list()

    def load_ignore_list(self):
        # ignore language specific features
        self.ignore_list_eu_ind = ['flesch_kincaid', 'dale_chall', 'smog', 'num_past', 'num_past_incidence', 'num_pres',
                                   'num_pres_incidence', 'num_future', 'num_future_incidence', 'num_past_irregular',
                                   'num_past_irregular_incidence', 'num_past_irregular_mean', 'num_first_pers_pron',
                                   'num_first_pers_pron_incidence', 'num_first_pers_sing_pron',
                                   'num_first_pers_sing_pron_incidence'
                                   'num_third_pers_pron', 'num_third_pers_pron_incidence', 'num_rel_subord',
                                   'num_rel_subord_incidence',
                                   'num_pass', 'num_pass_incidence', 'num_pass_mean', 'num_agentless',
                                   'agentless_passive_density_incidence',
                                   'num_ger', 'gerund_density_incidence', 'addition_connectives',
                                   'addition_connectives_incidence', 'consequence_connectives',
                                   'consequence_connectives_incidence', 'purpose_connectives',
                                   'purpose_connectives_incidence', 'illustration_connectives',
                                   'illustration_connectives_incidence', 'opposition_connectives',
                                   'opposition_connectives_incidence', 'order_connectives',
                                   'order_connectives_incidence', 'reference_connectives',
                                   'reference_connectives_incidence',
                                   'summary_connectives',
                                   'summary_connectives_incidence', 'num_content_words_not_a1_c1_words_incidence',
                                   # Se quitan hasta que esten validados
                                   'num_a1_words', 'num_a1_words_incidence', 'num_a2_words', 'num_a2_words_incidence',
                                   'num_b1_words', 'num_b1_words_incidence', 'num_b2_words', 'num_b2_words_incidence',
                                   'num_c1_words', 'num_c1_words_incidence', 'num_content_words_not_a1_c1_words'
                                   ]

        self.ignore_list_en_ind = ['addition_connectives',
                                   'addition_connectives_incidence', 'consequence_connectives',
                                   'consequence_connectives_incidence',
                                   'purpose_connectives', 'purpose_connectives_incidence', 'illustration_connectives',
                                   'illustration_connectives_incidence',
                                   'opposition_connectives', 'opposition_connectives_incidence', 'order_connectives',
                                   'order_connectives_incidence', 'reference_connectives',
                                   'reference_connectives_incidence', 'summary_connectives',
                                   'summary_connectives_incidence']

        self.ignore_list_es_ind = ['smog', 'num_rel_subord', 'num_rel_subord_incidence', 'num_pass',
                                   'num_pass_incidence',
                                   'num_pass_mean', 'num_agentless', 'agentless_passive_density_incidence',
                                   'logical_connectives',
                                   'logical_connectives_incidence',
                                   'adversative_connectives', 'adversative_connectives_incidence'
                                   # Se quitan hasta que esten validados
                                                              'num_a1_words', 'num_a1_words_incidence', 'num_a2_words',
                                   'num_a2_words_incidence',
                                   'num_b1_words', 'num_b1_words_incidence', 'num_b2_words', 'num_b2_words_incidence',
                                   'num_c1_words', 'num_c1_words_incidence', 'num_content_words_not_a1_c1_words'
                                   ]

        self.ignore_list_counters = ['prop', 'num_complex_words', 'num_words_more_3_syl', 'num_words',
                                     'num_different_forms',
                                     'num_words_with_punct', 'num_paragraphs', 'num_sentences', 'num_past', 'num_pres',
                                     'num_future',
                                     'num_indic', 'num_impera', 'num_past_irregular', 'num_past_irregular_incidence',
                                     'num_personal_pronouns', 'num_first_pers_pron', 'num_first_pers_sing_pron',
                                     'num_third_pers_pron', 'num_rare_nouns', 'num_rare_adj', 'num_rare_verbs',
                                     'num_rare_advb', 'num_rare_words', 'num_rare_words_incidence',
                                     'num_dif_rare_words',
                                     'num_dif_rare_words_incidence', 'num_a1_words', 'num_a2_words', 'num_b1_words',
                                     'num_b2_words',
                                     'num_c1_words', 'num_content_words_not_a1_c1_words', 'num_lexic_words', 'num_noun',
                                     'num_adj',
                                     'num_adv', 'num_verb', 'num_subord', 'num_rel_subord', 'num_total_prop',
                                     'noun_phrase_density_incidence', 'verb_phrase_density_incidence', 'num_pass',
                                     'num_pass_incidence', 'num_agentless', 'num_neg', 'num_ger', 'num_inf']

        self.similarity_list = ["similarity_adjacent_mean", "similarity_pairs_par_mean", "similarity_adjacent_par_mean",
                                "similarity_adjacent_std", "similarity_pairs_par_std", "similarity_adjacent_par_std"]

    def print_info(self):
        print("------------------------------------------------------------------------------")
        # print('Level of difficulty: ' + prediction[0].title())
        i = self.indicators
        # Anade en estas listas las que no quieras mostrar para todos los casos
        ignore_list = []

        if not self.similarity:
            ignore_list.extend(self.similarity_list)
        if self.language == "english":
            ignore_list.extend(self.ignore_list_en_ind)
        if self.language == "spanish":
            ignore_list.extend(self.ignore_list_es_ind)
        if self.language == "basque":
            ignore_list.extend(self.ignore_list_eu_ind)

        for key, value in self.ind_sentences.items():
            if key not in ignore_list:
                print(self.ind_sentences.get(key) + str(i.get(key)))

    # genera el fichero X.out.csv, MERECE LA PENA POR IDIOMA
    def generate_csv(self, csv_path, input, similarity):  # , csv_path, prediction, similarity):
        i = self.indicators
        # kk=prediction
        # estadisticos
        output = os.path.join(csv_path, os.path.basename(input) + ".out.csv")
        # Write all the information in the file
        estfile = open(output, "w")

        ignore_list = []

        if not self.similarity:
            ignore_list.extend(self.similarity_list)
        if self.language == "english":
            ignore_list.extend(self.ignore_list_en_ind)
        if self.language == "spanish":
            ignore_list.extend(self.ignore_list_es_ind)
        if self.language == "basque":
            ignore_list.extend(self.ignore_list_eu_ind)

        ref_per_features = ['num_words', 'lexical_density', 'flesch', 'num_personal_pronouns', 'num_past', 'min_wf_per_sentence '
                            , 'num_lexic_words', 'similarity_adjacent_mean', 'all_connectives', 'noun_overlap_adjacent']
        for key, value in self.ind_sentences.items():
            if key not in ignore_list:
                # Depende de la clave, habra que poner un texto u otro en referencia a los siguientes indicadores
                if key in ref_per_features:
                    self.print_feature_ref(estfile, key)
                estfile.write("\n%s" % self.ind_sentences.get(key) + str(i.get(key)))
        estfile.close()

    def print_feature_ref(self, estfile, key):
        if key == 'num_words':
            estfile.write("\n%s" % 'Shallow or descriptive measures')
        elif key == 'lexical_density':
            estfile.write("\n%s" % 'Lexical Richness/Lexical Density')
        elif key == 'flesch':
            estfile.write("\n%s" % 'Readability/Text Dimension/Grade Level')
        elif key == 'num_past':
            estfile.write("\n%s" % 'Morphological features')
        elif key == 'min_wf_per_sentence':
            estfile.write("\n%s" % 'Word Frequency')
        elif key == 'num_lexic_words':
            estfile.write("\n%s" % 'Syntactic Features / POS ratios')
        elif key == 'similarity_adjacent_mean':
            estfile.write("\n%s" % 'Semantic overlap')
        elif key == 'noun_overlap_adjacent':
            estfile.write("\n%s" % 'Referential cohesion')
        elif key == 'all_connectives':
            estfile.write("\n%s" % 'Connectives')

    # fichero csv para el aprendizaje automatico
    # ignore_list dauden ezaugarriak ez dira kontuan hartzen
    # concatena df=df+dfnew
    def write_in_full_csv(self, df, similarity, language, ratios):
        # Dictionaries (or dict in Python) are a way of storing elements
        # in a Python list using its index:my_list = ['p','r','o','b','e'] Output: 'p' using index my_list[0]
        # in a Python dict using a fixed key:a = {'apple': 'fruit', 'cake': 'dessert'}; a['doughnut'] = 'snack';print(a['apple'])
        # Keys must be unique, immutable objects, and are typically strings. The values in a dictionary can be anything. For many applications the values are simple types such as integers and strings.
        # the values in a dictionary are collections (lists, dicts, etc.) In this case, the value (an empty list or dict) must be initialized the first time a given key is used. While this is relatively easy to do manually, the defaultdict type automates and simplifies these kinds of operations.
        # from collections import defaultdict
        # self.indicators=defaultdict(float) ## default value of float is 0.0
        # self.indicators.items() ->
        i = self.indicators
        indicators_dict = {}
        headers = []
        # Anade en estas listas las que no quieras mostrar para todos los casos
        ignore_list = []

        if not similarity:
            ignore_list.extend(self.similarity_list)
        if ratios:
            ignore_list.extend(self.ignore_list_counters)
        if language == "english":
            ignore_list.extend(self.ignore_list_en_ind)
        if language == "spanish":
            ignore_list.extend(self.ignore_list_es_ind)
        if language == "basque":
            ignore_list.extend(self.ignore_list_eu_ind)

        for key, value in i.items():
            if key not in ignore_list:
                indicators_dict[key] = i.get(key)
                headers.append(key)
        # construct a new pandas dataframe from a dictionary: df = pd.DataFrame(data=[indicators_dict],columns=indicators_dict.keys()) columns: the column labels of the DataFrame.
        df_new = pd.DataFrame([indicators_dict], columns=indicators_dict.keys())
        # print(df_new)->  num_words  num_paragraphs  num_sentences
        # 0        100             1            13
        # Replace all NaN elements with 0s.
        df_new.fillna(0)
        # dataframe=dataframe+newdataframe
        df = pd.concat([df, df_new], sort=False)
        return df

    @staticmethod
    def create_directory(path):
        newPath = os.path.normpath(str(Path(path).parent.absolute()) + "/results")
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        return newPath

class Maiztasuna:
    freq_list = {}

    def __init__(self, path):
        self.path = path

    def load(self):
        with open(self.path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                Maiztasuna.freq_list[row[1].strip()] = row[0]


class Stopwords:
    stop_words = []

    def __init__(self, language):
        self.lang = language

    def print(self):
        for stopword in Stopwords.stop_words:
            print(stopword)

    def download(self):
        nltk.download('stopwords')

    #def load(self):
        #if self.lang == "english":
            #Stopwords.stop_words = stopwords.words('english')
        #if self.lang == "spanish":
            #Stopwords.stop_words = stopwords.words('spanish')
        #if self.lang == "basque":
            #Stopwords.stop_words = set(line.strip() for line in open('data/eu/StopWords/stopwords.txt', encoding='utf-8'))

    def load(self):
        if self.lang == "english":
            # Stopwords.stop_words = stopwords.words('english')
            # Open the file with read only permit
            f = open('data/en/StopWords/stopwords.txt', encoding='utf-8')
            # use readline() to read the first line
            line = f.readline()
            # use the read line to read further.
            # If the file is not empty keep reading one line
            # at a time, till the file is empty
            while line:
                # print(line)
                Stopwords.stop_words.append(line.strip())
                # use realine() to read next line
                line = f.readline()
            f.close()
            # Stopwords.stop_words = set(line.strip() for line in open('/var/www/html/erraztest/en/stopwords.txt'))
        if self.lang == "spanish":
            # Stopwords.stop_words = stopwords.words('spanish')
            # Open the file with read only permit
            f = open('data/es/StopWords/stopwords.txt', encoding='utf-8')
            # use readline() to read the first line
            line = f.readline()
            # use the read line to read further.
            # If the file is not empty keep reading one line
            # at a time, till the file is empty
            while line:
                # print(line)
                Stopwords.stop_words.append(line.strip())
                # use realine() to read next line
                line = f.readline()
            f.close()
            # Stopwords.stop_words = set(line.strip() for line in open('/var/www/html/erraztest/es/stopwords.txt'))
        if self.lang == "basque":
            # Open the file with read only permit
            f = open('data/eu/StopWords/stopwords.txt', encoding='utf-8')
            # use readline() to read the first line
            line = f.readline()
            # use the read line to read further.
            # If the file is not empty keep reading one line
            # at a time, till the file is empty
            while line:
                # print(line)
                Stopwords.stop_words.append(line.strip())
                # use realine() to read next line
                line = f.readline()
            f.close()
            # Stopwords.stop_words = set(line.strip() for line in open('/var/www/html/erraztest/eu/stopwords.txt'))
            # line.decode('utf-8').strip()


class Predictor:
    def __init__(self, language):
        self.lang = language
        self.clf = None
        self.selector = None

    def load(self):
        if self.lang == "english":
            # Para cargarlo, simplemente hacer lo siguiente:
            self.clf = joblib.load('./corpus/en/dataset_aztertest_full/classifier_aztertest_best.pkl')
            with open("./corpus/en/dataset_aztertest_full/selectorAztertestFullBest.pickle", "rb") as f:
                self.selector = pickle.load(f)

    def predict_dificulty(self, data):
        feature_names = data.columns.tolist()
        X_test = data[feature_names]
        # Para cargarlo, simplemente hacer lo siguiente:
        # se aplica el selector de atributos a los datos mediante el método transform()
        X_test_new = self.selector.transform(X_test)
        # y se realiza la predicción utilizando el método predict()
        return self.clf.predict(X_test_new)


class NLPCharger:

    def __init__(self, language, library, directory):
        # self.lang = language[0]
        self.lang = language
        # self.lib = library[0]
        self.lib = library
        self.dir = directory
        self.text = None
        self.textwithparagraphs = None
        self.parser = None

    '''
    Download the respective model depending of the library and language. 
    '''

    def download_model(self):
        if self.lib == "stanford":
            print("-----------You are going to use Stanford library-----------")
            if self.lang == "basque":
                print("-------------You are going to use Basque model-------------")
                MODELS_DIR = self.dir + '/eu'
                stanfordnlp.download('eu', MODELS_DIR)  # Download the Basque models
            elif self.lang == "english":
                print("-------------You are going to use English model-------------")
                MODELS_DIR = self.dir + '/en'
                print("-------------Downloading Stanford English model-------------")
                stanfordnlp.download('en', MODELS_DIR)  # Download the English models
            elif self.lang == "spanish":
                print("-------------You are going to use Spanish model-------------")
                MODELS_DIR = self.dir + '/es'
                stanfordnlp.download('es', MODELS_DIR)  # Download the Spanish models
            else:
                print("........You cannot use this language...........")
        elif self.lib == "cube":
            print("-----------You are going to use Cube Library-----------")
        else:
            print("You cannot use this library. Introduce a valid library (Cube or Stanford)")

    '''
    load model in parser object 
    '''

    def load_model(self):
        if self.lib == "stanford":
            print("-----------You are going to use Stanford library-----------")
            if self.lang == "basque":
                print("-------------You are going to use Basque model-------------")
                # MODELS_DIR = 'J:\TextSimilarity\eu'
                MODELS_DIR = self.dir + '/eu'
                #               config = {'processors': 'tokenize,pos,lemma,depparse',  # Comma-separated list of processors to use
                #                           'lang': 'eu',  # Language code for the language to build the Pipeline in
                #                           'tokenize_model_path': MODELS_DIR + '\eu_bdt_models\eu_bdt_tokenizer.pt',
                #                           # Processor-specific arguments are set with keys "{processor_name}_{argument_name}"
                #                           'pos_model_path': MODELS_DIR + '\eu_bdt_models\eu_bdt_tagger.pt',
                #                           'pos_pretrain_path': MODELS_DIR + '\eu_bdt_models\eu_bdt.pretrain.pt',
                #                           'lemma_model_path': MODELS_DIR + '\eu_bdt_models\eu_bdt_lemmatizer.pt',
                #                           'depparse_model_path': MODELS_DIR + '\eu_bdt_models\eu_bdt_parser.pt',
                #                           'depparse_pretrain_path': MODELS_DIR + '\eu_bdt_models\eu_bdt.pretrain.pt'
                #                          }
                config = {'processors': 'tokenize,pos,lemma,depparse',  # Comma-separated list of processors to use
                          'lang': 'eu',  # Language code for the language to build the Pipeline in
                          'tokenize_model_path': MODELS_DIR + '/eu_bdt_models/eu_bdt_tokenizer.pt',
                          # Processor-specific arguments are set with keys "{processor_name}_{argument_name}"
                          'pos_model_path': MODELS_DIR + '/eu_bdt_models/eu_bdt_tagger.pt',
                          'pos_pretrain_path': MODELS_DIR + '/eu_bdt_models/eu_bdt.pretrain.pt',
                          'lemma_model_path': MODELS_DIR + '/eu_bdt_models/eu_bdt_lemmatizer.pt',
                          'depparse_model_path': MODELS_DIR + '/eu_bdt_models/eu_bdt_parser.pt',
                          'depparse_pretrain_path': MODELS_DIR + '/eu_bdt_models/eu_bdt.pretrain.pt'
                          }
                self.parser = stanfordnlp.Pipeline(**config)

            elif self.lang == "english":
                print("-------------You are going to use English model-------------")
                MODELS_DIR = self.dir + '/en'
                config = {'processors': 'tokenize,mwt,pos,lemma,depparse',  # Comma-separated list of processors to use
                          'lang': 'en',  # Language code for the language to build the Pipeline in
                          'tokenize_model_path': MODELS_DIR + '/en_ewt_models/en_ewt_tokenizer.pt',
                          'pos_model_path': MODELS_DIR + '/en_ewt_models/en_ewt_tagger.pt',
                          'pos_pretrain_path': MODELS_DIR + '/en_ewt_models/en_ewt.pretrain.pt',
                          'lemma_model_path': MODELS_DIR + '/en_ewt_models/en_ewt_lemmatizer.pt',
                          'depparse_model_path': MODELS_DIR + '/en_ewt_models/en_ewt_parser.pt',
                          'depparse_pretrain_path': MODELS_DIR + '/en_ewt_models/en_ewt.pretrain.pt'
                          }
                self.parser = stanfordnlp.Pipeline(**config)
            elif self.lang == "spanish":
                print("-------------You are going to use Spanish model-------------")
                MODELS_DIR = self.dir + '/es'
                config = {'processors': 'tokenize,pos,lemma,depparse',  # Comma-separated list of processors to use
                          'lang': 'es',  # Language code for the language to build the Pipeline in
                          'tokenize_model_path': MODELS_DIR + '/es_ancora_models/es_ancora_tokenizer.pt',
                          # Processor-specific arguments are set with keys "{processor_name}_{argument_name}"
                          'pos_model_path': MODELS_DIR + '/es_ancora_models/es_ancora_tagger.pt',
                          'pos_pretrain_path': MODELS_DIR + '/es_ancora_models/es_ancora.pretrain.pt',
                          'lemma_model_path': MODELS_DIR + '/es_ancora_models/es_ancora_lemmatizer.pt',
                          'depparse_model_path': MODELS_DIR + '/es_ancora_models/es_ancora_parser.pt',
                          'depparse_pretrain_path': MODELS_DIR + '/es_ancora_models/es_ancora.pretrain.pt'
                          }
                self.parser = stanfordnlp.Pipeline(**config)
            else:
                print("........You cannot use this language...........")
        elif self.lib == "cube":
            print("-----------You are going to use Cube Library-----------")
            if self.lang == "basque":
                # initialize it
                cube = Cube(verbose=True)
                # load(self, language_code, version="latest",local_models_repository=None,
                # local_embeddings_file=None, tokenization=True, compound_word_expanding=False,
                # tagging=True, lemmatization=True, parsing=True).
                # Ejemplo:load("es",tokenization=False, parsing=False)
                ## select the desired language (it will auto-download the model on first run)
                cube.load("eu", "latest")
                self.parser = cube
            elif self.lang == "english":
                cube = Cube(verbose=True)
                cube.load("en", "latest")
                self.parser = cube
            elif self.lang == "spanish":
                cube = Cube(verbose=True)
                cube.load("es", "latest")
                self.parser = cube
            else:
                print("........You cannot use this language...........")
        else:
            print("You cannot use this library. Introduce a valid library (Cube or Stanford)")

    def process_text(self, text):
        self.text = text.replace('\n', '@')
        self.text = re.sub(r'@+', '@', self.text)
        # separa , . ! ( ) ? ; del texto con espacios, teniendo en cuenta que los no son numeros en el caso de , y .
        self.text = re.sub(r"\_", " ", self.text)
        # self.text = re.sub(r'[.]+(?![0-9])', r' . ', self.text)
        # self.text = re.sub(r'[,]+(?![0-9])', r' , ', self.text)
        self.text = re.sub(r"!", " ! ", self.text)
        self.text = re.sub(r"\(", " ( ", self.text)
        self.text = re.sub(r"\)", " ) ", self.text)
        self.text = re.sub(r"\?", " ? ", self.text)
        self.text = re.sub(r";", " ; ", self.text)
        self.text = re.sub(r"\-", " - ", self.text)
        self.text = re.sub(r"\—", " - ", self.text)
        self.text = re.sub(r"\“", " \" ", self.text)
        self.text = re.sub(r"\”", " \" ", self.text)
        # sustituye 2 espacios seguidos por 1
        self.text = re.sub(r"\s{2,}", " ", self.text)
        return self.text

    '''
    Transform data into a unified structure.
    '''

    def get_estructure(self, text):
        self.text = text
        # Loading a text with paragraphs
        self.textwithparagraphs = self.process_text(self.text)
        # Getting a unified structure [ [sentences], [sentences], ...]
        return self.adapt_nlp_model()

    def adapt_nlp_model(self):
        ma = ModelAdapter(self.parser, self.lib)
        return ma.model_analysis(self.textwithparagraphs, self.lang)


class Pronouncing:
    # Pronunciador(the Carnegie Mellon Pronouncing Dictionary)- Utilizado para obtener silabas: pip install cmudict
    # cmudict is a pronouncing dictionary for north american english words.
    # it splits words into phonemes, which are shorter than syllables.
    # (e.g. the word 'cat' is split into three phonemes: K - AE - T).
    # but vowels also have a "stress marker":
    # either 0, 1, or 2, depending on the pronunciation of the word (so AE in 'cat' becomes AE1).
    # the code in the answer counts the stress markers and therefore the number of the vowels -
    # which effectively gives the number of syllables (notice how in OP's examples each syllable has exactly one vowel)
    # from nltk.corpus import cmudict
    # pronunciation dictionary
    # prondict = cmudict.dict()
    prondict = {}

    #def __init__(self, language):
    #    self.lang = language

    def load(self):
        Pronouncing.prondict = cmudict.dict()

    def euskara_text2syllables(self, textwithoutpuuntuation):
        #elif self.lang == "basque":
        # #accedemos a foma
        # command_01 = "foma"
        # os.system(command_01)
        #
        # #utilizamos el script silabaEus que contendra las reglas
        # command_02 = "source silabaEus.script"
        # os.system(command_02)
        # Write all the information in the file
        # genera CADENAS aleatorias
        #import uuid
        silaba_name = str(uuid.uuid4())
        silaba_name = silaba_name+"_silaba.txt"
        # Creamos un fichero con las palabras divididas en silabas por puntos
        with open(silaba_name, "w", encoding="utf-8") as f:
            for word in text_without_punctuation:
                command = "echo " + word.text + " | flookup -ib data/eu/syllablesplitter/silabaEus.fst"
                subprocess.run(command, shell=True, stdout=f)
            # Tratamos el fichero y guardamos en un diccionario cada palabra
        with open(silaba_name, mode="r", encoding="utf-8") as f:
            for linea in f:
                if not linea == '\n':
                   str = linea.rstrip('\n')
                   palabra_sin_puntos_rep = str.replace('.', '')  # [txakurra txakurra, ... , ...]
                   line = palabra_sin_puntos_rep.split('\t')  # [ [txakurra, txakurra], [..,..], ...]
                   palabra = line[0]
                   num_sil = []  # se crea para utilizar la misma estructura que cmudict.dict()
                   num_sil.append(len(str.split('.')))
                   Pronouncing.prondict[palabra] = num_sil  # [txakurra] = 3
        os.system("rm " + str(silaba_name))
    def print(self):
        for k, v in Pronouncing.prondict.items():
            print(k, v)


"This is a Singleton class which is going to start necessary classes and methods."


# from packageDev.Charger import NLPCharger
# import re

class Main(object):
    __instance = None

    def __new__(cls):
        if Main.__instance is None:
            Main.__instance = object.__new__(cls)
        return Main.__instance

    def extract_text_from_file(self, input):
        # Si el fichero de entrada no tiene extension .txt
        if ".txt" not in input:
            # textract extrae el texto de todo tipo de formatos (odt, docx, doc ..)
            pre_text = textract.process(input)
            # decode(encoding='UTF-8',errors='strict') convierte a utf8 y si no puede lanza un error
            text = pre_text.decode()
        else:
            # Si extensión .txt convierte texto a utf-8
            with open(input, encoding='utf-8') as f:
                text = f.read()
        return text

    def start(self):

        #####Argumentos##################################
        from argparse import ArgumentParser
        # ArgumentParser con una descripción de la aplicación
        p = ArgumentParser(description="python3 ./main.py -f \"laginak/*.doc.txt\" ")
        # Grupo de argumentos requeridos
        required = p.add_argument_group('required arguments')
        required.add_argument('-f', '--files', nargs='+',
                              help='Files to analyze (in .txt, .odt, .doc or .docx format)')
        required.add_argument('-l', '--language', help='Language to analyze (english, spanish, basque)')
        required.add_argument('-m', '--model', help='Model selected to analyze (stanford, cube)')
        required.add_argument('-d', '--directory', help='Work directory($HOME)')
        # Grupo de argumentos opcionales
        optional = p.add_argument_group('optional arguments')
        optional.add_argument('-c', '--csv', action='store_true', help="Generate a CSV file")
        optional.add_argument('-r', '--ratios', action='store_true', help="Generate a CSV file only with ratios")
        optional.add_argument('-s', '--similarity', action='store_true', help="Calculate similarity (max. 5 files)")
        # Por último parsear los argumentos
        opts = p.parse_args()

        language = opts.language
        #language = "spanish"
        print("language:", str(language))
        # language = "english"
        model = opts.model
        #model = "stanford"
        print("model:", str(model))
        directory = opts.directory
        #directory=directorylist[0]
        print("directory:",str(directory))
        similarity = opts.similarity
        #similarity = False
        print("similarity:", str(similarity))
        csv = opts.csv
        print("csv:", str(csv))
        ratios = opts.ratios
        print("ratios:", str(ratios))


        # Carga wordfrequency euskara
        if language == "basque":
            maiztasuna = Maiztasuna("data/eu/Maiztasunak/LB2014Maiztasunak_zenbakiakKenduta.csv")
            maiztasuna.load()

        # Connectives
        conn = Connectives(language)
        conn.load()

        # Carga Niveles Oxford
        if language == "english":
            ox = Oxford()
            ox.load()

        # Carga verbos irregulares
        if language != "basque":
            ir = Irregularverbs(language)
            ir.load()

        # Carga StopWords
        stopw = Stopwords(language)
        stopw.download()
        stopw.load()
        # stopw.print()

        # Load Pronouncing Dictionary
        if language == "english":
            prondic = Pronouncing()
            prondic.load()
            #prondic.print()

        # Carga del modelo Stanford/NLPCube
        cargador = NLPCharger(language, model, directory)
        cargador.download_model()
        cargador.load_model()

        # Predictor
        predictor = Predictor(language)
        predictor.load()

        files = opts.files

        # @staticmethod
        # def load_files(args):
        #    FileLoader.files = args
        #    print("Parametros: " + str(FileLoader.files))

        #files = ["vlad.txt"] #euskaratestua Loterry-adv
        print("Files:" + str(files))
        ### Files will be created in this folder
        path = Printer.create_directory(files[0])
        print("Path:" + str(path))
        df_row = None
        for input in files:
            # # texto directamente de text
            # if language == "basque":
            #     text = "ibon hondartzan egon da. Eguraldi oso ona egin zuen.\nHurrengo astean mendira joango da. "                "\n\nBere lagunak saskibaloi partidu bat antolatu dute 18etan, baina berak ez du jolastuko. \n "                "Etor zaitez etxera.\n Nik egin beharko nuke lan hori. \n Gizonak liburua galdu du. \n Irten hortik!"                    "\n Emadazu ur botila! \n Zu beti adarra jotzen."
            # if language == "english":
            #     text = "ibon is going to the beach. I am ibon. \n"                 "Eder is going too. He is Eder."
            # if language == "spanish":
            #     text = "ibon va ir a la playa. Yo soy ibon. \n"                 "Ibon tambien va a ir. El es Ibon."
            # texto directamente de fichero
            text = self.extract_text_from_file(input)

            # Get indicators
            document = cargador.get_estructure(text)
            indicators = document.get_indicators(similarity)
            printer = Printer(indicators, language, similarity)
            printer.load_ind_sentences()
            printer.print_info()
            printer.generate_csv(path, input, similarity)  # path, prediction, opts.similarity)
            if csv:
                df_row = printer.write_in_full_csv(df_row, similarity, language, ratios)
        if csv:
            df_row.to_csv(os.path.join(path, "full_results_aztertest.csv"), encoding='utf-8', index=False)


main = Main()
main.start()