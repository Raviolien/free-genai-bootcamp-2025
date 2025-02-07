# Homework sentence constructor

## Chosen language
I have chosen to work with French as I know some French and know absolutely no Japanese. 

## Models
I'm using the free tier. 

### ChatGPT 
It tells me it runs GPT-4-turbo. I also tested on GPT-3.5 as I hit the limit of free uses on GPT-4

### Mistral AI 
It didn't specify what model it is using

### Meta AI 
Apparently not available in my country (Denmark)

### Anthropic Claude
Claude 3.5 Haiku

### DeepSeek
DeepSeek-V3 and DeepThink (R1)


## How I did

### Creating the prompt document
- First, I created a prompt document that worked with ChatGPT 4o, where I define "worked" as providing the vocabulary table, sentence structure, clues, extra clues upon student's request, feedback and further clues upon student's attempts, and verrification of correct translation by the student as I would like them to be. 
- As I ran out of free tier usage of 4o, the prompt document was also tested on GPT 3.5. For this model to work extra examples needed to be added. 
- Next, I added to the prompt document so it worked with Mistral AI
- Next, I ran the prompt document with Claude, where it worked well without further adjustments
- Last, I ran the prompt document with DeepSeek, where it worked well without further adjustments

#### Notes
- chat gpt: 4o works really well with the prompt script, it gives clues that are helpfull without giving away the answer. 3.5 first run with the script that worked with 4o, the model gave translations in the clues. Works well after giving some more examples of what not to put in the clues

- meta ai: not available in Denmark

- mistral ai: needed to log in to have a chat and not just a one-time answer (i.e. stuck in Step "Initiate"). It gives pronouns in the vocabulary table even though asked not to. 
It reproduced the same clues over and over again and the clues are not really helpfull. It also gave clues to words that the student translated correctly. After adding two more instructions to #Steps of interactions it informed the student about correct parts (which is nice). Handles misspelling bad (by giving clues about something completly different).
Ran into limit of free usage pretty fast.

- chatGPT adopted (ran the prompt script after changes done for mistral ai) the part on informing about right parts nicely. Misspellings handled better, but is not understood as a misspelling (to instead of tu)

- Anthropic Claude: 
Step "Initial" works with the prompt scrip (i.e. gives the wanted vocabulary table and relevant and understandable clues). However, when asked for more clues it provides examples that are the correct translation of the student sentence - the examples are a good idea but should be unrelated to the student sentence. 
Ignores the misspelling of "To" (should be tu). Added "be mindfull of student mispelling". 


## Further work (wanted to but didn't have time)
Take the final version of the prompt document and run again with all AI assistents and do same input sentence and same tranlation attempts to test the different steps with the different AI assistents. 
