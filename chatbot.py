# Names: Aashritha Ananthula and Zen Park
# Project 2 - Chatbot
# Chatbot Topic: CatBot prints cat facts, cat jokes, and converses with its user through a rules based approach!

# import libraries
import nltk
import re
import pickle
import random
import numpy as np
import wikipedia
import time
import textwrap
import os.path

from urllib import request
from bs4 import BeautifulSoup

from nltk.corpus import stopwords

bot_name = 'CatBot: '
user_model = {}

# get a url and extract information from the url
def webcrawl(link):
    # extracting starter url
    html = request.urlopen(link).read().decode('utf8')
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    # split into sentences
    text = text[500:]
    raw_sentences = text_chunks = [c for c in text.splitlines() if not re.match(r'^\s*$', c)]

    processed_facts = []

    # I processed text by restricting facts and jokes to be greater than 5 words and less than 40 words
    # I also removed sentences with the token 'ways' to avoid irrelavant text such as '7 ways to...'
    for s in raw_sentences:
        temp = s.lower()
        tokens = temp.split()
        if len(tokens) > 5 and len(tokens) < 40 and 'ways' not in tokens:
            processed_facts.append(s)

    #print(len(processed_facts))
    return processed_facts

# adds list into a file pickled
def pickle_write(filename, list):
    with open(filename, 'wb') as fp:
        pickle.dump(list, fp)

# unpickles file with a list and returns the list
def pickle_read(filename):
    with open (filename, 'rb') as fp:
        list = pickle.load(fp)
    return list

# remove punctuation, spaces, lowercase user input
def parse_response(user_input):
    parsed_response = re.split(r'\s+|[,.:;/?\'\"\\*-+()&^%$#@!`~]\s*', user_input.lower())

# This function collects information about the user such as name and age and stores them in the user model
def user_intro():
    print('Hello, Welcome to Catbot!\nTo quit, type \'bye\' or \'quit\' or  \'exit\'\n')

    # ask user for name, age, and personal information
    user_name = input('Catbot: What is your name?\nYou: ')

    quit = ['bye', 'exit', 'quit']
    # Exisiting users, their data is in the user model
    if user_name in user_model:
        print(f"Catbot: Hi {user_name}, you're back!!")

    elif user_name.lower() in quit:
        print("Bye!")
        return -1

    # New Users, data not in user model
    else:
        user_age = input(f'Catbot: Hi {user_name}! How old are you?\nYou: ')
         # save user's name and age in the user_model dict
        temp  = {'Age': str(user_age)}
        user_model[user_name] = temp
        print("Catbot: Cool, Do you have any questions for me?")

    return user_name

# randomly prints a sentence from a list, used to print responses based on the rules
def getRandomData(list):
    rand_index = random.randint(0,len(list)-1)
    return list[rand_index]

# compares 2 sentences using the cosine similarity formula
def cosine_similarity(sent_a, sent_b):
    stop_words = stopwords.words('english')

    # remove stop words from sentences and lowercase
    tok_a = {w for w in sent_a if not w in stop_words}
    tok_b = {w for w in sent_b if not w in stop_words}

    l_a = []
    l_b = []
    vector = tok_a.union(tok_b)
    for i in vector:
        if i in tok_a:
            l_a.append(1)
        else:
            l_a.append(0)
        if i in tok_b:
            l_b.append(1)
        else:
            l_b.append(0)

    c = 0
    for i in range(len(vector)):
        c+= l_a[i]*l_b[i]

    if c==0:
        return 0
    cosine = c / float((sum(l_a)*sum(l_b))**0.5)
    return cosine

# checks the similarities of a list full of sentences and stores their similarity value
def similarity_list(list, user_input):
    vals = []
    for l in list:
        vals.append(cosine_similarity(l, user_input))
    return max(vals)

# returns the index of the question with the most similarity compared to the user input
def similarity_dict(responses, user_input):
    vals = []
    for l1,l2 in responses:
        if len(l1) > 1:
            max_sim = similarity_list(l1, user_input)
            # if max similarity of the user input to all rules is less than 0.2, do a web search
            if max_sim <= 0.2:
                return -1
            else:
                vals.append(max_sim)
        else:
            temp_list = []
            temp_list.append(l1)
            max_sim = cosine_similarity(temp_list, user_input)
            # if max similarity of the user input to all rules is less than 0.2, do a web search
            if max_sim <=0.2:
                print(max_sim)
                return -1
            else:
                vals.append(max_sim)

    n = np.array(vals)
    # return max similarity
    return np.argmax(n)

# This function searches a string on the web and gets the first few sentences about this topic on the web
def wikipedia_search(query):
    # time.sleep(1)
    print('Let me look that up for you! Here is a wikipedia article:')
    try:
        # time.sleep(2)
        print(textwrap.fill(wikipedia.summary(query, sentences=2) + '\n'))
    except:
        # dealing with questions that chatbot doesn't have response to
        time.sleep(1)
        print('.')
        time.sleep(1)
        print('.')
        print("I couldn't find anything.")
        pass

# This function contains all the rules and how the chatbot processes the different types of user input
def chat_user(jokelist, factlist, user_name):

        # Rules
        responses = [
        [
            ["hi", "hello", "sup", "hey", "hola", "howdy"],
            [ "Hello friend!",  "Hi there!", "Hola amiga!", "Hey there!"]
        ],
        # [
        #     ["help", "help me"],
        #     ["I can help you ", "No, let me help you", "I can't help you"]
        # ],
        [
            ["how old are you", "old"],
            ["Just 2 weeks", "Ask my creator"]
        ],
        [
            ["who made you", "who is your creator"],
            ["I was created by Aashritha and Zen.", "I do not know"]
        ],
        [
            ["your name", "what is your name", "who are you", "what"],
            ["My name is CatBot, meow!", "Hi, I'm CatBot, meow!"]
        ],
        [
            ["how are you", "what's up", "what are you doing"],
            ["I'm just living in your computer "  + user_name]
        ],
        [
            ["joke", "tell me a joke", "what's a joke", "do you know a joke", "funny", "you're funny", "say a cat joke"],
            jokelist
        ],
        [
            ["fact", "tell me a fact", "what's a fact", "cat fact", "say a cat fact"],
            factlist
        ],
        [
            ["do you love me", "i love you", "will you marry me", "are you single"],
            ["I am incapable of love.", "No, sorry, I am married to Alexa."]
        ],
        [
            [r"you are", r"you're"],
            ["I know", "I'm aware", "I know, meow!"]
        ],
        [
            ["you're dumb", "you're stupid", "you're bad", "mad", "angry", "this bot is stupid", "insult me"],
            ["That's not very nice " + user_name, "*sad cat noises* meow :("]

        ],
        [
            ["I like", "I love"],
            ["Cool, me too", "And I love you, meow!", "I love it too!", "I love cats!"]
        ],
        [
            ["I hate", "I dislike"],
            ["Me too " + user_name, "How do you hate?", "And I hate it too!"]
        ],
        [
            ["i'm", "im", "feel"], ["I don't feel"]
        ],
        [
            ["hi", "hello"],
            [ "Hello friend!",  "Hi there!", "Hola amiga!", "Hey there!"]
        ],
        [
            ["are you sentient", "are you a robot", "are you real", "are you a human"],
            [ "Perhaps? I enjoy telling jokes and facts.", "You decide! *meows in beeps*"]
        ],
        [
            ["what can you do", "what are you capable of", "help", "help me", "commands"],
            [ "Ask me for a cat joke! Ask me for a cat fact! Or ask me about the buttered cat paradox!"]
        ],
        [
            ["cool", "nice", "wow"],
            [ "I know right!",  "Any more questions for me?", "meow..."]
        ]
    ]

        quit=["quit", "exit", "bye"]
        bot_name = "CatBot: "
        user_input = ""

        while user_input not in quit:
            user_input = quit
            try:
                user_input = input("You: ")
            except EOFError:
                print(user_input)
            if user_input:
                while user_input[-1] in "!.":
                    user_input = user_input[:-1]
                #print(user_input)

                user_input = user_input.lower()

                # If the keyword like or love is found in the user input, we store what the
                # user likes in the user model
                if 'like' in user_input or 'love' in user_input:
                    tokens = user_input.split(" ")
                    if 'like' in user_input:
                        num = tokens.index("like")
                    elif 'love' in user_input:
                        num = tokens.index("love")
                    likes = ""
                    for i in tokens[num+1:]:
                        likes += i
                        likes += " "

                    # append what the user likes to the user model
                    if 'likes' in user_model[user_name]:
                        (user_model[user_name])['likes'].append(likes)
                    else:
                        (user_model[user_name])['likes'] = [likes]

                     # Also, add this response to the rule answers to personalize the bot
                    print(bot_name + getRandomData((responses[11])[1]))
                    (responses[11])[1].append('I know you love ' + likes + "too, " + user_name + "!")

                # If the keyword hate or dislike is found in the user input, we store what the
                # user hates in the user model
                elif 'hate' in user_input or 'dislike' in user_input:
                    tokens = user_input.split(" ")
                    if 'hate' in user_input:
                        num = tokens.index("hate")
                    else:
                        num = tokens.index("dislike")
                    dislikes = ""
                    for i in tokens[num+1:]:
                        dislikes += i
                        dislikes += " "
                    #print(num)
                    #print(dislikes)

                    # append what the user hates to the user model
                    if 'hates' in user_model[user_name]:
                        (user_model[user_name])['hates'].append(dislikes)
                    else:
                        (user_model[user_name])['hates'] = [dislikes]

                    print(bot_name + getRandomData((responses[12])[1]))

                    # Also, add this response to the rule answers to personalize the bot
                    (responses[12])[1].append('I know you hate ' + dislikes + "too, " + user_name + "!")

                # if user says bye, quit, or exit, stop running the program
                elif user_input in quit:
                    print('Bye ' + user_name + ", see you later!")

                # For all other user outputs, look at the rules dict, compute cosine similarity, and
                # choose the most relavant output
                else:
                    num = similarity_dict(responses, user_input)
                    # If the similarities are too low, look up the user input on wikipedia and return the response
                    if num == -1 and user_input not in (responses[0])[0]:
                        wikipedia_search(user_input)
                    # If we found a matching response in our rules, print one of those answers randomly
                    else:
                        print(bot_name + getRandomData((responses[num])[1]))

if __name__ == '__main__':

    # If user model exists, read from it
    if os.path.exists('user_model.p'):
        with open('user_model.p', 'rb') as handle:
            user_model = pickle.load(handle)
            #print(user_model)

    # get cat facts and write to knowledge base
    cat_fact_list = webcrawl('https://cvillecatcare.com/veterinary-topics/101-amazing-cat-facts-fun-trivia-about-your-feline-friend/#:~:text=Cats%20are%20believed%20to%20be,to%20six%20times%20their%20length.')
    pickle_write('catfacts.p', cat_fact_list)
    factlist = pickle_read('catfacts.p')
    factlist = factlist[:101]
    #print(getRandomData(factlist))


    # get cat jokes and write to knowledge base
    cat_jokes_list = webcrawl('https://bestlifeonline.com/cat-jokes/')
    pickle_write('catjokes.p', cat_jokes_list[1:40])
    jokelist = pickle_read('catjokes.p')

    # get user info
    user_name = user_intro()
    if user_name != -1:
        # chat with user unit they quit
        chat_user(jokelist, factlist, user_name)


    # write user model dict to file and read it when we run the program again
    with open('user_model.p', 'wb') as handle:
        pickle.dump(user_model, handle, protocol=pickle.HIGHEST_PROTOCOL)


