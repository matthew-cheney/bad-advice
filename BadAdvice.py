import nltk
import mlconjug
from nltk.stem import WordNetLemmatizer
import random

class BadAdvice:

    def __init__(self):
        self.default_conjugator = mlconjug.Conjugator(language='en')
        self.lemmatizer = WordNetLemmatizer()

        # self.lemma_exceptions = {'am': 'be', 'are': 'be', 'is': 'be'}
        self.lemma_exceptions = {}
        self.prons_to_flip = {'your': 'my', 'my': 'your', 'yours': 'mine', 'mine': 'yours', 'there': 'here', 'here': 'there'}


    def get_advice(self, sent):
        # sent = sent.lower()
        tagged_toks = self._get_tagged_toks(sent)
        # tagged_toks = self._to_lower(tagged_toks)
        tagged_toks[0] = (tagged_toks[0][0].lower(), tagged_toks[0][1])
        tagged_toks[1] = (tagged_toks[1][0].lower(), tagged_toks[1][1])

        if tagged_toks[0][1] == 'MD':
            return self._get_modal_answer(tagged_toks)
        else:
            return self._get_other_answer(tagged_toks)

    def _get_tagged_toks(self, sent):
        toks = nltk.word_tokenize(sent)
        tagged_toks = nltk.pos_tag(toks)
        return tagged_toks

    def _get_modal_answer(self, tagged_toks):
        temp = tagged_toks[0]
        tagged_toks[0] = tagged_toks[1]
        tagged_toks[1] = temp  # There is probably a better way to swap these
        tagged_toks[0] = (
        self._flip_pronoun(tagged_toks[0][0]), tagged_toks[0][1])
        # tagged_toks[1] = (self._flip_noun(tagged_toks[1][0], self._get_person(tagged_toks[0][0])), tagged_toks[1][1])
        tagged_toks = self._flip_remaining_prons(tagged_toks, 2)
        return self._yes_or_no(tagged_toks)

    def _get_other_answer(self, tagged_toks):
        temp = tagged_toks[0]
        tagged_toks[0] = tagged_toks[1]
        tagged_toks[1] = temp  # There is probably a better way to swap these
        tagged_toks[0] = (self._flip_pronoun(tagged_toks[0][0]), tagged_toks[0][1])
        tagged_toks[1] = (self._flip_noun(tagged_toks[1][0], self._get_person(tagged_toks[0][0])),tagged_toks[1][1])
        tagged_toks = self._flip_remaining_prons(tagged_toks, 2)
        return self._yes_or_no(tagged_toks)

    def _yes_or_no(self, tagged_toks):
        if random.random() < .5:
            tagged_toks.insert(0, ('Yes,', ''))
        else:
            tagged_toks.insert(0, ('No,', ''))
            tagged_toks.insert(3, ('not', ''))
        return self._format_advice(tagged_toks)

    def _format_advice(self, tagged_toks):
        if tagged_toks[len(tagged_toks) - 1][1] == '.':
            del tagged_toks[-1]
        full_sentence = ' '.join([x[0] for x in tagged_toks])
        full_sentence += '.'
        full_sentence = full_sentence.capitalize()
        return full_sentence

    def _to_lower(self, tagged_toks):
        for i in range(len(tagged_toks) - 1):
            if tagged_toks[i][1].startswith('NNP'):
                tagged_toks[i] = (tagged_toks[i][0].capitalize(), tagged_toks[i][1])
            else:
                tagged_toks[i] = (tagged_toks[i][0].lower(), tagged_toks[i][1])
        return tagged_toks

    def _flip_pronoun(self, pronoun):
        if pronoun == 'you':
            return 'I'
        if pronoun == 'i':
            return 'you'
        return pronoun

    def _flip_noun(self, noun, needed_pos):
        if noun in self.lemma_exceptions.keys():
            lemma = self.lemma_exceptions[noun]
        else:
            lemma = self.lemmatizer.lemmatize(noun, pos='v')
        toReturn = self.default_conjugator.conjugate(lemma).conjug_info['indicative']['indicative present'][needed_pos]
        return toReturn

    def _get_person(self, person_in):
        first_singulars = ['i', 'I']
        second_singulars = ['you']
        first_plurals = ['we']
        second_plurals = ['yall', 'y\'all']

        first_sing_tag = '1s'
        second_sing_tag = '2s'
        third_sing_tag = '3s'
        first_plur_tag = '1p'
        second_plur_tag = '2p'
        third_plur_tag = '3p'

        if person_in in first_singulars:
            return first_sing_tag
        if person_in in second_singulars:
            return second_sing_tag
        if person_in in first_plurals:
            return first_plur_tag
        if person_in in second_plurals:
            return second_plur_tag
        return third_sing_tag

    def _flip_remaining_prons(self, tagged_toks, starting_index):
        for i in range(starting_index, len(tagged_toks)):
            if tagged_toks[i][0] in self.prons_to_flip:
                tagged_toks[i] = (self.prons_to_flip[tagged_toks[i][0]], tagged_toks[i][1])
        return tagged_toks