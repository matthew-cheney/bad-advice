import random

import nltk

class BadAdviceCFG:
    def __init__(self):
        self.auxiliaries = {'can', 'do', 'are', 'should', 'is', 'does'}
        self.master_auxiliary = ()
        self.master_noun_phrase = list()
        self.master_verb_phrase = list()
        self.tagged_tokens = list()
        pass

    def get_advice(self, sent):
        self.master_auxiliary = list()
        self.master_noun_phrase = list()
        self.master_verb_phrase = list()
        self.noun_post_head = list()

        sent = sent.lower()
        self.tagged_toks = self._tokenize(sent)
        success = self._find_auxiliary(self.tagged_toks, self.master_auxiliary)
        if not success:
            return "not a valid auxiliary"
        success = self._find_NP(self.tagged_toks, self.master_noun_phrase)
        if not success:
            return "not a valid noun phrase"
        success = self._find_VP(self.tagged_toks, self.master_verb_phrase)
        if not success:
            return "not a valid verb phrase"

        # toReturn = f'aux: {self._reconstruct_sentence(self.master_auxiliary)}\n' \
        #            f'NP: {self._reconstruct_sentence(self.master_noun_phrase)}\n' \
        #            f'VP: {self._reconstruct_sentence(self.master_verb_phrase)}'

        return self._build_advice(self.master_auxiliary, self.master_noun_phrase, self.master_verb_phrase)

    def _tokenize(self, sent):
        toks = nltk.word_tokenize(sent)
        tagged_toks = nltk.pos_tag(toks)
        return tagged_toks

    def _find_auxiliary(self, tagged_toks, collector):
        if tagged_toks[0][0] in self.auxiliaries:
            collector.append(tagged_toks.pop(0))
            return True
        else:
            return False

    def _find_NP(self, tagged_toks, collector):
        self._find_pre_head(tagged_toks, collector)
        self._find_noun_head(tagged_toks, collector)
        noun_post_head = list()
        if len(tagged_toks) > 0:
            self._find_post_head(tagged_toks, collector, noun_post_head)
            collector.extend(noun_post_head)
        return True

    def _find_VP(self, tagged_toks, collector):
        collector.extend(tagged_toks)
        return True  # Temporary solution

        self._find_verb(tagged_toks, collector)
        if tagged_toks[0][1].startswith('N'):
            self._find_NP(tagged_toks, collector)
        elif tagged_toks[0][1].startswith('P'):
            self._find_prepositional_phrase(tagged_toks, collector)
        return True

    def _find_pre_head(self, tagged_toks, collector):
        if tagged_toks[0][1] == 'DT':
            collector.append(tagged_toks.pop(0))
        if not tagged_toks[0][1].startswith('N') and not tagged_toks[0][1].startswith('P'):
            collector.append(tagged_toks.pop(0))
            return self._find_pre_head(tagged_toks, collector)
        return True

    def _find_noun_head(self, tagged_toks, collector):
        if tagged_toks[0][1].startswith('N') or \
                tagged_toks[0][1].startswith('P'):
            collector.append(tagged_toks.pop(0))
        return True

    def _find_post_head(self, tagged_toks, collector, post_head_collector):
        if tagged_toks[0][1] == 'IN' and not tagged_toks[0][0] == 'like':
            self._find_prepositional_phrase(tagged_toks, post_head_collector)
            new_sent = self._reconstruct_sentence(collector) + ' ' + self._reconstruct_sentence(tagged_toks)
            toks = nltk.word_tokenize(new_sent)
            tagged_toks = nltk.pos_tag(toks)
        return True

    def _find_prepositional_phrase(self, tagged_toks, collector):
        if tagged_toks[0][1] == 'IN':
            collector.append(tagged_toks.pop(0))
            self._find_NP(tagged_toks, collector)
        return True

    def _find_verb(self, tagged_toks, collector):
        if tagged_toks[0][1].startswith('V') or tagged_toks[0][0] == 'like':
            collector.append(tagged_toks.pop(0))
            return True
        else:
            return False

    def _reconstruct_sentence(self, tagged_toks):
        return ' '.join([x[0] for x in tagged_toks])

    def _build_advice(self, auxiliary, noun_phrase, verb_phase):
        if random.random() < .5:
            advice = 'no, '
            advice += self._reconstruct_sentence(noun_phrase) + ' '
            advice += self._reconstruct_sentence(auxiliary)
            advice += ' not '
            advice += self._reconstruct_sentence(verb_phase)
        else:
            advice = 'no, '
            advice += self._reconstruct_sentence(noun_phrase) + ' '
            advice += self._reconstruct_sentence(auxiliary)
            advice += ' not '
            advice += self._reconstruct_sentence(verb_phase)
        return advice