import re
from collections import Counter
from config import Config

class Signals:
    def __init__(self):
        self.debugging_counter = 1
    
    def sequence(self, text):
        result = {
            "score": 0.0,
            "signal1_score": 0.0,
            "signal2_score": 0.0,
            "reasons": {}
        }
        signal1 = self.one(text)
        signal2 = self.two(text)
        result['reasons'] = {
            "signal1": [reason for reason in signal1['reasons']], 
            "signal2": [reason for reason in signal2['reasons']]
            }

        
        overall_score = (signal1['score'] * 0.5) + (signal2['score'] * 0.5)
        result['score'] = overall_score
        result['signal1_score'] = signal1['score']
        result['signal2_score'] = signal2['score']
        return result
        
    def breakdown_text(self, text: str):
        
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s for s in sentences if s.strip()]
        lengths = [len(s.split()) for s in sentences] # each sentence being split

        # Clean words
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).lower().split()

        return {
        "text": cleaned,
        "word_count": len(cleaned),
        "sentence_length": len(sentences),
        "lengths": lengths,
        "paragraph_count": len(sentences) / 4,
        "characters_including_spaces": len(text),
        "characters_excluding_spaces": len(text.replace(" ", ""))
    }
    
    def isbetween(self, count, choice="limit") -> bool | dict[str, bool]:
        commons = {
            "limit": Config.COMMON_AI_WORD_COUNT_LIMIT,
            "paragraph": Config.COMMON_AI_WORD_COUNT_PARAGRAPTH,
            "sentence": Config.COMMON_AI_WORD_COUNT_SENTENCE,
        }
        
        if choice == "all":
            result = {}
            for key, val in result.items():
                
                result[key] = val[0] < count < val[1] # low end < the count < high end
            return result 
        
        if choice not in commons.keys():
            print(f"THE WORD '{choice}' IS NOT KNOWN INSIDE THE SYSTEM")
            return False
        
        choice = commons[choice.lower().strip()]
        return choice[0] < count < choice[1] # low end < the count < high end
    
    def quick_calc(self, result, word_count, choice:str="limit"):
        # result = {
        #     "score":  0.0,
        #     "reasons": []
        # }
        
        between = self.isbetween(word_count, choice=choice)
        if isinstance(between, bool) and between:
            result['score'] += 10.0
            result['reasons'].append(f"The word count of the text falls between the average legnth for ai generated {choice}")
        
        if isinstance(between, dict):
            for key, var in between.items():
                if var:
                    result['score'] += 10.0
                    result['reasons'].append(f"The word count of the text falls between the average legnth for ai generated {key}")
        
            
        return result
            
            
    def one(self, text):
        """
        This is signal 1. We are checking the length of the text, if any words repeat, 
        then return a list of suspicions
        

        Args:
            text: Users text
        """
        
        # TEST: 2728 characters, 436 words, 'the' repeats 40 times which is 1.46% of the text, 9.17% of the wording
     
        result = {
            "score": 0.0,
            "reasons": []
        }
        

        text_breakdown = self.breakdown_text(text)
        breakdown_counter = Counter(text_breakdown['text'])

        word_count = text_breakdown['word_count'] 
        most_common = breakdown_counter.most_common()
        
        first_3 = 0
        for count in most_common:
            if count[1] < 2:
                continue
            result['score'] += (count[1] / word_count) * 100
            if first_3 < 3:
                result['reasons'].append(f"The word '{count[0]}' repeats {count[1]} times, which is {count[1] / word_count * 100} of the text.")
            first_3 += 1
            
        result = self.quick_calc(result, word_count=word_count)
        result['score'] = float(result['score'] / 100)
        
        return result
        
        
        
        
    def two(self, text):
        result = {
            "score": 0.0,
            "reasons": []
        }
        
        text_breakdown = self.breakdown_text(text)

        lengths = text_breakdown['lengths'] # pretty much a list of sentences split
        if len(lengths) == 0:
            return result
        
        word_count = sum(lengths)
        avg = word_count / len(lengths) # average length of sentences

        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths) # (the length of current sentence - the median length of sentences to the power of 2) - the amount of sentences
    
        normalized = 1 / (1 + variance)

        result["score"] = float(normalized)

        # Reasoning
        result["reasons"].append(
            f"Sentence length variance is {variance:.2f}, indicating {'uniform' if variance < 5 else 'varied'} structure."
        )

        return result
    
    def three(self, ai_response: dict):
        
    # refernce 
    
    # low = 10, medium = 20, high = 33 
    # {
    #     "repetition_low_high": "low|medium|high",
    #     "structure_uniformity_low_high": "low|medium|high",
    #     "predictability_low_high": "low|medium|high"
    # }
        result = {
            "score": 0.0,
            "reason": [],
        }
        
        amounts = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }
        # if all 3 are 'high', that'll be 99, which ends up being 0.495 in scoring. 
        # I found this ideal, as it's not guaranteed that text is AI, but in this range it's highly likely. 
        # This score added to the first 2 signals leaves huge impact.
        
        observed_signals = ai_response['observed_signals']
        
        repetition_low_high = observed_signals['repetition_low_high']
        structure_uniformity_low_high = observed_signals['structure_uniformity_low_high']
        predictability_low_high = observed_signals['predictability_low_high']
        
        aoc = Counter([repetition_low_high, structure_uniformity_low_high, predictability_low_high])
        
        most_common = aoc.most_common()
        
        reduction = 0
        # reduction system. Lets say all the obverations are low,
        # process looks like this:
        #   3 (all 3 are lows) / 3 (3 options) * 0.5 (reducing the float) / 2 (avoid extreme changes)
        # = -0.166
        # (low, 2), (high, 1)
        # score = 53 + -0.166 = 0.364
        if len(most_common) < 3:
            if most_common[0][0] == 'low':
                reduction = -((most_common[0][1] / 3) * 0.5) / 2
                
            if most_common[0][0] == 'high':
                reduction = ((most_common[0][1] / 3) * 0.5) / 2
            
            if most_common[0][0] == 'medium':
                if len(most_common) > 1:
                    if most_common[1][0] == "high":
                        reduction = 0.2
                    elif most_common[1][0] == "low":
                        reduction = -0.15
                else:
                    reduction = 0.1
        print(f"FINAL REDUCTION: {reduction}")
        result['score'] += amounts[repetition_low_high]
        self._debug_scores(result['score'])
        result['score'] += amounts[structure_uniformity_low_high]
        self._debug_scores(result['score'])
        result['score'] += amounts[predictability_low_high]
        self._debug_scores(result['score'])
        result['score'] = (float(result['score']) * 0.5) / 100
        self._debug_scores(result['score'])
        result['score'] = float(result['score'] + reduction)
        self._debug_scores(result['score'])
        result["reason"] = f"{ai_response['vocabulary_notes']}. {ai_response['sentence_structure_notes']}. {ai_response['stylistic_notes']}"
    
        return result
    
    def _debug_scores(self,score):
        print(f"[DBUG {self.debugging_counter}] SCORE: \u2022{score}\n")
        self.debugging_counter += 1
if __name__ in "__main__":
    signal = Signals()
    
    # Story created by Gemini for quick testing
    
    test = """
    
    The afternoon light over the Charles River was fading into a deep shade of twilight. 
    Elian tucked his collar against the crisp autumn breeze as he walked the familiar path toward the 
    Boston Public Library in Copley Square. He was supposed to be returning a biography on maritime 
    history, but the city had a way of pulling him off his usual route.
    Instead, he found himself ducking down Province Street, drawn by the warm glow of an antiquarian 
    bookshop he had never noticed before. 
    The bell above the door chimed a soft, dissonant note as he stepped inside.
    The air was thick with the scent of old paper and roasted coffee beans.
    "Looking for anything specific?" a voice asked from behind a towering stack of leather-bound journals.
    The shopkeeper, an elderly woman with silver hair and wire-rimmed glasses, peered over her books.
    "Not really," Elian admitted, trailing a finger along a dusty wooden shelf. 
    "Just exploring."The woman nodded knowingly and gestured to the back corner. 
    "Try the bottom shelf in the shadow of the ladder.
    I think you'll find what you didn't know you were looking for.
    "Elian navigated the narrow aisles, the wooden floorboards creaking beneath his boots.
    He knelt in the dim light and reached for a heavy, 
    cloth-bound volume sandwiched between two newer-looking books.
    When he pulled it out, a cloud of dust danced in a stray beam of sunlight. 
    The cover bore no title, just an embossed silver compass rose.
    He opened it to the middle pages, expecting to see a faded map or an old ledger. 
    Instead, he found a collection of intricate, 
    hand-drawn charcoal sketches depicting places he had visited, but with impossible details woven 
    into them. A sketch of the Boston Public Garden showed the iconic weeping willows,
    but nestled in the branches were glowing, bioluminescent flowers."What is this place?" 
    Elian whispered, tracing his finger over the textured paper.
    "It is a record of the places that exist in the spaces between," 
    the shopkeeper said, appearing quietly beside him. 
    "The city you see every day is just the backdrop. The magic lies in the details.
    "He looked up, a dozen questions forming on his lips, 
    but the woman simply smiled and took the book from his hands, 
    replacing it with a quiet grace. "Come back when you are ready to see the real city," 
    she said.Dazed, Elian stepped back out onto the bustling street. 
    The familiar city skyline suddenly felt different, 
    like a stage waiting for the curtain to rise. 
    He looked toward the river, 
    wondering what other hidden landscapes were waiting to be discovered just out of sight.
    
    """.strip() # scores 0.60 for signal.one()
    
    
    test2 = """
    
    When Clara was 9 years old, she was riding her bicycle down a steep hill in her hometown of Burlington, MA, when she lost control, broke her arm, and hit her head on the pavement. Panicked and in tears, she didn't know what to do until a kind neighborhood boy roughly her age rushed over, helped her up, and walked her home. She never learned his name, but she always remembered his bright orange windbreaker.Fast forward twenty years. Clara was grabbing coffee in Boston to celebrate a promotion with her best friend, Sarah. Sarah had brought along an old college acquaintance named Mark. As the three of them chatted and caught up, the conversation shifted to childhood memories, and Clara brought up her infamous bike accident as a funny, nostalgic story.As she detailed the crash and the bright orange jacket, Mark went completely silent. He reached into his wallet, pulled out a small, faded Polaroid of himself as a 9-year-old in that exact orange windbreaker, and said, "Clara, I think I’m the boy who walked you home".They were both completely stunned. The boy who had helped her in her time of need two decades ago was now sitting across the table. They spent the rest of the evening talking, connecting the dots of their shared childhoods, and realizing how perfectly their paths aligned.They started dating shortly after and eventually got married, turning an accidental childhood encounter into a lifelong love story.
    
    
    """.strip()
    
    test3 = "I love eating alot of foods and just hanging out with friends.".strip() # Created by me, scores 0.0, meaning no way this is "AI"
    
    test4 = "The afternoon sunlight filtered through the trees, casting slow-moving shadows across the quiet street.".strip() # made by chatgpt, scores 0.2
    
    test5 = "The afternoon drifted by with a calm, unhurried rhythm as a light breeze moved through the trees and stirred the leaves into soft motion. Birds called out intermittently from the branches, breaking the quiet in brief, scattered moments before the sound settled again. On the sidewalk, a few people walked at an easy pace, lost in their own thoughts, while distant traffic hummed like a steady background note. Everything felt ordinary yet peaceful, as if the day itself had paused just long enough to be noticed.".strip()
    
    test6 = """Mara found the key on a rainy Tuesday, stuck between the pages of a library book she was returning late. It was small, old, and oddly warm in her palm, as if it had been waiting for her specifically. There was no label, no tag, nothing to suggest what it opened—only a faint engraving of a spiral on its head.

Curiosity won out over common sense. That evening, she walked through her neighborhood until she noticed a narrow door she had never seen before wedged between two brick buildings. It didn’t belong to any shop she recognized, and there was no sign above it. The key fit perfectly.

Inside was not a room, but a long hallway lined with doors—dozens, maybe hundreds—each one slightly different in shape and color. Some hummed softly. Others were silent, as if holding their breath. Mara stepped forward slowly, realizing each door seemed to react to her presence, as though they had been waiting just as long as the key had.

She didn’t open any of them that night. Instead, she closed the door behind her, keeping the key in her pocket, understanding suddenly that some discoveries aren’t meant to be rushed—they’re meant to be returned to, one choice at a time.
""".strip()

    test7 = """Medium is a home for human stories and ideas. Here, anyone can share knowledge and wisdom with the world—without having to build a mailing list or a following first. The internet is noisy and chaotic; Medium is quiet yet full of insight. It’s simple, beautiful, collaborative, and helps you find the right readers for whatever you have to say.



Ultimately, our goal is to deepen our collective understanding of the world through the power of writing.


We believe that what you read and write matters. Words can divide or empower us, inspire or discourage us. In a world where the most sensational and surface-level stories often win, we’re building a system that rewards depth, nuance, and time well spent. A space for thoughtful conversation more than drive-by takes, and substance over packaging.


Over 100 million people connect and share their wisdom on Medium every month. They’re software developers, amateur novelists, product designers, CEOs, and anyone burning with a story they need to get out into the world. They write about what they’re working on, what’s keeping them up at night, what they’ve lived through, and what they’ve learned that the rest of us might want to know too.


Instead of selling ads or selling your data, we’re supported by a growing community of over a million Medium members who believe in our mission. If you’re new here, start reading. Dive deeper into whatever matters to you. Find a post that helps you learn something new, or reconsider something familiar—and then write your story."""
    
    
    
    test8 = """
    
    Nobody really prepares you for parenthood. You can read all the books and take all the classes, then still feel like you’re falling short when you have an actual little girl in front of you.

I was doing it all on my own.

Bath time, bedtime, homeschooling. It takes a toll. Sometimes I wish that it wasn’t like this, but other times I take pride in knowing I’m bringing her up all by myself.

Unfortunately, as she grows older, navigating becomes incredibly difficult. There’s just some things that she needs her mom for.

It’s not like I don’t try. I try and get her things I think she’d enjoy. Baby dolls, stuffed animals, tea sets. That kind of thing.

It’s just not enough. The older she gets, the more she misses her mom. I always found it strange. I mean, there’s no possible way she can remember her.

She always asks when she’s coming back. When she gets to see her again. Why I don’t let her have friends. Why it seems like I don’t let her go outside.

This isn’t something I can say I accounted for.
When I took her, as much as it hurts to admit, it was more impulse than anything. I wanted a little girl of my own.

I always struggled with women. Having children always felt like a fantasy. It just kept building and building until I couldn’t control myself anymore.
When I saw her unattended at the park, it was like my body acted before my mind did.

She was just a baby. No more than a few months old. I wanted to give her the life that I so desperately felt the need to provide.

But now I think I’m realizing what kind of mistake that really was. We don’t even feel close anymore. She’s distant. It’s like she knows. It’s almost like she’s terrified of me.

Part of me wants to give her back. I just don’t think I can.

She’s nearly 8 years old now. At least, somewhere within that range. Her mom wouldn’t even recognize her.

Then again, maybe she would.

So many feelings.

I don’t know.

Maybe I’ll just keep her for a few more years.

I still have so much to teach her.
    """.strip() # r/stories, scores 0.80 for signal.one()
    
    
    test9 = """I’m in angst. That’s the only way I know how to describe it. Everything just feels so surreal right now.

My wife and I have been together for the last 35 years. We married young and had our daughter around 10 years later.

I still remember the day she had to be taken to the hospital. I was at work when her water broke, but instead of calling and demanding I get there as soon as possible, she told me that it was best I wait and that she was doing completely fine.

I told her she was crazy if she thought I wasn’t gonna be there for the birth of my child, but she started screaming at me to stay where I was. I just chalked it up to birth hormones.

I finished out the day, and as soon as I clocked out, I was flying to the hospital.

It was a venture that proved fruitless, as when I arrived, my wife was nowhere to be found. And in the chaos of the busy hospital, my panic grew more and more until my pager started beeping.

It was my wife’s number, and in a confused hurry, I found the nearest phone to take her call.

She was already home, asking me where I had been.

After a little back and forth about the sheer audacity of that statement, I got in my car and drove home as quickly as I could.

When I got there, I found her curled up in her chair in the living room, cradling our baby and looking both exhausted and completely drained.

Under normal circumstances, this should’ve been one of the happiest moments of my life. But, really, all I felt was confusion.

Why? Because we were scheduled to have a baby boy for her entire pregnancy. That’s what the doctors kept telling us.

Her explanation was that there had been some kind of mistake with the paperwork. Pretty expensive mistake, I guess, because we had spent hundreds on clothes and toys for a boy.

I still allowed myself to feel happy. I mean, I was a new father. I’d waited 9 months for this moment. I wasn’t gonna let some paperwork issue rain on my parade. Besides, her mom seemed in no mood to argue.

I spent the entire first night back home curled up in bed with my wife and our baby girl. I soothed them to sleep in each other’s arms. I rubbed my wife’s back. I held the baby when she cried. It was the start of our new life.

From that moment on, I worked my ass off to give them a decent life. Kept food on the table, kept the lights on in the house. I’d even save up every month for big gifts like jewelry and swing sets.

Watching my daughter grow up was one of the most magical experiences of my life. Watching her go from her first steps to her first day of school. Seeing her grow into a blossoming young woman and eventually walking across the stage for her high school graduation.

It was weird, though. Nobody ever said we looked alike. Nobody ever said she and her mom even looked alike. And, if I’m being honest, I thought the same thing, but it didn’t change how I loved her.

But, unfortunately, every fairy tale must come to an end, and ours ended with her mom being diagnosed with cancer. Those were some of the most difficult years of my life. Watching the woman I love lose her appetite. Lose her hair. Lose her life. It broke something within me.

I was by her side every day, right there with my daughter.

However, on the day we lost her, my daughter had been in class at the state university a hundred miles away, and I was all alone, watching the world crumble before my very eyes.

In those last moments, she looked at me with the same love she had back when we first met. Only this time, it was more reminiscent. More sad. Like she was realizing that everything was coming to an end.

And that’s when her face changed.

Her smile faded.

Her forehead creased.

She started sobbing.

The words she spoke next are what have sent me over the edge. I’ve been questioning our relationship, our life, and everything in between ever since. I want to say I was lost, but, truthfully, it made everything make sense.

Because according to my wife:

Our son died at birth after some complications.

I guess something snapped in her mind when she was told that her baby didn’t make it.

Instead of accepting, she rejected.

My daughter was stolen.

And I still haven’t found the heart to tell her.""".strip() # r/stores, scores 0.71 for signal.one()

# FLAW: I believe for signal.one(), the longer the story or text, the higher the score is for part 1 which means the longer -> the more likely it's seen as "AI" which is flawed in most context. BUT r/stories can be filled with fake stories
    result = signal.sequence(test8)
    # counts = signal.one(test)
    # print(counts)
    
    
    ai_response_test = {'vocabulary_notes': "The text features a diverse vocabulary with descriptive phrases, such as 'deep shade of twilight', 'crisp autumn breeze', and 'warm glow of an antiquarian bookshop'. There is a notable absence of repetitive words or phrases.", 
                        'sentence_structure_notes': 'The sentence structure is varied, with a mix of short and long sentences that create a sense of rhythm and flow. The use of descriptive passages and dialogue adds to the dynamic nature of the structure.', 
                        'stylistic_notes': "The text is rich in stylistic features, including personal experience, specificity, and detailed phrasing. The author's use of sensory details, such as the 'scent of old paper and roasted coffee beans', creates a vivid and immersive atmosphere.", 
                        'observed_signals': {'repetition_low_high': 'low', 
                                             'structure_uniformity_low_high': 'high', 
                                             'predictability_low_high': 'high'}}
    
    ai_response = signal.three(ai_response=ai_response_test)
    print(ai_response)
    
    print(f"\nSEQUENCE SCORES: \n\t- signal 1 {result['signal1_score']} \n\t- signal 2 {result['signal2_score']} \n\t- OVERALL {result['score']} \n\t- AI {ai_response['score']}")
    fs = float(min(result['score'] + ai_response['score'], 1.0))
    print(f"\nFINAL SCORE: {fs}")