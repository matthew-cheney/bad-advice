import random

import nltk
from mlconjug import mlconjug


class BadAdviceCFG:
    def __init__(self):

        self.default_conjugator = mlconjug.Conjugator(language='en')
        self.lemmatizer = nltk.WordNetLemmatizer()

        self.auxiliaries = {'is', 'am', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does', 'did', 'could', 'would', 'should', 'may', 'must', 'might', 'can', 'will', 'won\'t'}
        self.prons_to_flip = {'your': 'my', 'my': 'your', 'yours': 'mine', 'mine': 'yours', 'there': 'here', 'here': 'there', 'me': 'you', 'you': 'me', 'I': 'you', 'i': 'you'}
        self.single_verb_exceptions = {'there'}
        self.non_conjugating_verbs = {'should', 'would', 'could'}
        '''        self.master_auxiliary = ()
        self.master_noun_phrase = list()
        self.master_verb_phrase = list()
        self.tagged_tokens = list()
        self.master_pronoun = list()'''
        self.flippable_pronouns = {'i', 'you'}

        self.yes_pres = [
            'Yes, ',
            'Hm... I am going to go with yes, ',
            'It is a close one, but yes, ',
            'I do not understand why this is so important to you, but yes, ',
            'Of course, '
        ]

        self.no_pres = [
            'No, ',
            'Most definitely not, ',
            'There is no way, ',
            'Not by a longshot. No, ',
            'I am positive that no, '
        ]

        self.after_advice = [
            '.',
            '. Everybody knows that.',
            '. Why would you even ask such a question?',
            '. At least, I think so.',
            '. But do no take my word for it.',
            '. Without a doubt.'
        ]

    def get_advice(self, sent):
        try:
            advice = self._get_advice(sent)
        except Exception:
            advice = 'No. Next question.'
        return advice

    def _get_advice(self, sent):
        self.master_auxiliary = list()
        self.master_noun_phrase = list()
        self.master_verb_phrase = list()
        self.noun_post_head = list()
        self.master_pronoun = list()

        sent = sent.lower()
        self.tagged_toks = self._tokenize(sent)
        success = self._find_auxiliary(self.tagged_toks, self.master_auxiliary)
        if not success:
            return "not a valid auxiliary"
        success = self._find_NP(self.tagged_toks, self.master_noun_phrase)
        if not success:
            return "not a valid noun phrase"
        if len(self.tagged_toks) == 0:
            self._retract_VP_PP(self.master_noun_phrase, self.master_verb_phrase)
        else:
            success = self._find_VP(self.tagged_toks, self.master_verb_phrase)
            if not success:
                return "not a valid verb phrase"

        # toReturn = f'aux: {self._reconstruct_sentence(self.master_auxiliary)}\n' \
        #            f'NP: {self._reconstruct_sentence(self.master_noun_phrase)}\n' \
        #            f'VP: {self._reconstruct_sentence(self.master_verb_phrase)}'

        # return toReturn
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
        if tagged_toks[0][0] in self.flippable_pronouns:
            self.master_pronoun.append(tagged_toks.pop(0))
            self.master_noun_phrase = self.master_pronoun
            return True
        if tagged_toks[0][0] in self.single_verb_exceptions:
            self.master_noun_phrase.append(tagged_toks.pop(0))
            return True
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
        if tagged_toks[0][1] == 'DT' or tagged_toks[0][1] == 'PRP$':
            collector.append(tagged_toks.pop(0))
        if not tagged_toks[0][1].startswith('N') and not tagged_toks[0][1].startswith('P'):
            collector.append(tagged_toks.pop(0))
            return self._find_pre_head(tagged_toks, collector)
        return True

    def _find_noun_head(self, tagged_toks, collector):
        if tagged_toks[0][1].startswith('N') or \
                tagged_toks[0][1] == 'PRP':
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

        if verb_phase[len(verb_phase) - 1][1] == '.':
            del verb_phase[-1]

        if len(self.master_pronoun) > 0:
            noun_phrase = list()
            noun_phrase.append(self._flip_pronoun(self.master_pronoun[0]))
            new_pos = self._get_person(noun_phrase[0][0])
            new_aux = (self._flip_verb(auxiliary[0][0], new_pos), new_pos)
            auxiliary.clear()
            auxiliary.append(new_aux)

        noun_phrase = self._flip_remaining_prons(noun_phrase, 0, True)
        verb_phase = self._flip_remaining_prons(verb_phase, 0, False)

        auxiliary = self._capitalize(auxiliary)
        noun_phrase = self._capitalize(noun_phrase)
        verb_phase = self._capitalize(verb_phase)

        if random.random() < .5:
            yes = False
        else:
            yes = True
        advice = self._get_pre_advice(yes)
        advice += self._reconstruct_sentence(noun_phrase) + ' '
        advice += self._reconstruct_sentence(auxiliary)
        if not yes:
            advice += ' not '
        else:
            advice += ' '
        advice += self._reconstruct_sentence(verb_phase)
        advice += self._get_after_advice()
        advice = advice[0].upper() + advice[1:]
        return advice

    def _flip_pronoun(self, pronoun):
        if pronoun[0] == 'you':
            return ('I', pronoun[1])
        if pronoun[0] == 'i':
            return ('you', pronoun[1])
        return pronoun

    def _flip_verb(self, verb, needed_pos):
        if verb in self.non_conjugating_verbs:
            return verb
        lemma = self.lemmatizer.lemmatize(verb, pos='v')
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

    def _flip_remaining_prons(self, tagged_toks, starting_index, skipFirst):
        for i in range(starting_index, len(tagged_toks)):
            if tagged_toks[i][0] in self.prons_to_flip:
                if skipFirst:
                    skipFirst = False
                    continue
                tagged_toks[i] = (self.prons_to_flip[tagged_toks[i][0]], tagged_toks[i][1])
        return tagged_toks

    def _retract_VP_PP(self, noun_phrase, verb_phrase):
        for each in noun_phrase[-1::-1]:
            verb_phrase.insert(0, each)
            noun_phrase.remove(each)
            if each[1] == 'IN':
                break
        return

    def _capitalize(self, tagged_toks):
        toReturn = list()
        for tok, tag in tagged_toks:
            if tok == 'i':
                toReturn.append((tok.upper(), tag))
            elif tag.startswith('NNP'):
                toReturn.append((tok.capitalize(), tag))
            else:
                toReturn.append((tok, tag))
        return toReturn

    def _get_pre_advice(self, yes):
        if yes:
            return self.yes_pres[random.randint(0, len(self.yes_pres) - 1)]
        else:
            return self.no_pres[random.randint(0, len(self.no_pres) - 1)]

    def _get_after_advice(self):
        return self.after_advice[random.randint(0, len(self.after_advice) - 1)]