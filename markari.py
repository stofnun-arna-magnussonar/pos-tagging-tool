#!/usr/bin/env python3

from tkinter import *
import tkinter as tk
from tkinter import filedialog
import codecs
import os
from functools import partial
import datetime
from tkinter.messagebox import showinfo
import time
import webbrowser



#download and install pillow:
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
#from PIL import Image, ImageTk

class SearchResults:

    def __init__(self):
        self.sent_ids = []
        self.part_ids = {}
        self.line_nrs = {}
        self.nrs = {} # keeps track of number of each result
        self.index = 0
        self.p_index = 0
        self.line_index = 0
        self.length = 0
        self.nr = 0

    #bæta leitarniðurstöðum við
    def add(self, sent_id, part_id, line_nr):

        self.nr+=1
        if sent_id not in self.sent_ids:
            self.sent_ids.append(sent_id)
            self.part_ids[sent_id]= []

        if part_id not in self.part_ids[sent_id]:
            self.part_ids[sent_id].append(part_id)

        tmp_id = "{}_{}".format(sent_id, part_id)
        if tmp_id not in self.line_nrs:
            self.line_nrs[tmp_id] = []
            self.nrs[tmp_id] = []

        self.line_nrs[tmp_id].append(line_nr)
        self.nrs[tmp_id].append(self.nr)
        self.length+=1

    #skilar leitaniðurstöðum miðað við núverandi index
    def get(self):

        sent_id = self.sent_ids[self.index]
        part_id = self.part_ids[sent_id][self.p_index]
        tmp_id = "{}_{}".format(sent_id, part_id)
        line_nrs = self.line_nrs[tmp_id]
        return [sent_id, part_id, line_nrs]

    #receives index of sentence and part and returns results
    def get_by_indices(self, index, p_index):

        id = "{}_{}".format(index, p_index)
        if id in self.line_nrs:
            return self.line_nrs[id]
        return []

    def _get_sent_id(self):

        return self.sent_ids[self.index]

    def next(self):

        if self.nr>self.length:
            self.nr = 1
        sent_id = self._get_sent_id()

        #next line if threre is another in
        #next part if still in sentence
        if self.p_index<len(self.part_ids[sent_id])-1:
            self.p_index+=1
        else:

            #next sentence if there is any
            if self.index < len(self.sent_ids)-1:
                self.index+=1
                self.p_index = 0
            else:
                self.index= 0
                self.p_index = 0

        self.set_nr()

    #gives a value to self.nr depending on value in self.nrs = nr of search result of the first line on page
    def set_nr(self):
        self.nr = self.nrs[self.get_id()][self.line_index]

    def prev(self):
        self.nr-=1
        if self.nr==0:
            self.nr = self.length
        sent_id = self._get_sent_id()
        if self.p_index>0:
            self.p_index-=1
        else:
            if self.index > 0:
                self.index-=1
                sent_id = self._get_sent_id()
                self.p_index = len(self.part_ids[sent_id])-1
            else:
                self.index = len(self.sent_ids)-1
                sent_id = self._get_sent_id()
                self.p_index = len(self.part_ids[sent_id])-1

        self.set_nr()

    #set index and p_index of next search result
    def set_indices(self, index, p_index):

        if len(self.sent_ids)==0:
            return

        for i in range(0, len(self.sent_ids)):
            if self.sent_ids[i]>=index:
                self.index = i
                break

        if len(self.sent_ids)>0:
            sent_id = self.sent_ids[self.index]

            for i in range(0, len(self.part_ids[sent_id])):
                if self.part_ids[sent_id][i]>=p_index:
                    self.p_index = i
                    break

        self.nr = self.nrs[self.get_id()][self.line_index]


    def get_id(self):

        sent_id = self.sent_ids[self.index]
        part_id = self.part_ids[sent_id][self.line_index]
        return "{}_{}".format(sent_id, part_id)

    def get_length(self):
        return len(self.sent_ids)

    def do_print(self):

        for i in range(0, len(self.sent_ids)):
            sent_id  = self.sent_ids[i]

            part_ids = self.part_ids[sent_id]

            for j in range(0, len(part_ids)):
                part_id = part_ids[j]
                tmp_id = "{}_{}".format(sent_id, part_id)
                str = ""
                str+="{}: = {} ".format(j, part_id)
                for nr in self.line_nrs[tmp_id]:
                    str+="{} ".format(nr)
            print("{}: = Sent_id: {}".format(i, sent_id))
            print("\t"+str)

class Search():

    def __init__(self):
        self.results = None
        self.index = 0
        self.string = ""

    def clear(self):
        self.results = None
        self.index = 0
        self.string = ""

    #receives index of sentence and part and returns results
    def get_by_indices(self,index, p_index):

        if self.results is not None:
            return self.results.get_by_indices(index, p_index)
        else:
            return []

    #when clicked on >
    def next(self, string):

        if self.results is None or self.results.length==0:
            self.search(string)
        else:
            self.results.next()


    def prev(self, string):

        if self.results is None or self.results.length==0:
            self.search(string)
        else:
            self.results.prev()


    def search(self, string):

        self.results = SearchResults()
        self.string = string
        fields = []
        search_terms = []
        self.index=0

        splt = string.split("&&")
        for part in splt:
            splt2 = part.split("=")
            if len(splt2)!=2:
                errorMsg = "Leitarstrengur er ekki á réttu formati."
                print(errorMsg)
                app.msgLabel_v.set(errorMsg)
                return

            fields.append(splt2[0].strip())
            search_terms.append(splt2[1].strip())


        if self._search(fields, search_terms):

            if self.results.get_length()==0:
                app.writeMsg("Ekkert fannst", "red")
                print("Ekkert fannst")

                self.results.do_print()


    def _search(self, fields, search_terms):

        indices = []

        if len(fields)!=len(search_terms):
            errorMsg = "Leitarstrengur er ekki á réttu formati."
            app.writeMsg(errorMsg, "red")
            return False

        for i in range(0, len(fields)):

            if fields[i] not in ["tag","remark","wordform","mark","ath","orðmynd","orð","done","lokið","lemma"]:
                errorMsg = "Aðeins er hægt að leita eftir tag (mark), lemma, remark (ath), wordform (orðmynd) og done (lokið)"
                app.writeMsg(errorMsg, "red")
                return False

            else:

                if fields[i]=="tag" or fields[i]=="mark":
                    indices.append(tag_i)
                elif fields[i]=="wordform" or fields[i]=="orðmynd" or fields[i]=="orð":
                    indices.append(wordform_i)
                elif fields[i]=="lemma":
                    indices.append(lemma_i)
                elif fields[i]=="remark" or fields[i]=="ath":
                    indices.append(remark_i)
                elif fields[i]=="done" or fields[i]=="lokið":
                    indices.append(done_i)

        for i in range(0, data.length): #ítra yfir allar setningar
            if data.sentences[i].is_sentence: #ef um raunverulega setningu er að ræða
                parts = data.sentences[i].get_parts()
                for j in range(0, len(parts)): #ítra yfir parta setningar

                    for k in range(0, len(parts[j])):
                        line = parts[j][k]
                        if self.match(line, fields, search_terms, indices):
                            self.results.add(i, j, k)


        self.results.set_indices(data.index, data.p_index)
        return True

    def match(self, line, fields, search_terms, indices):

        for i in range(0, len(fields)):
            re_comp = re.compile(r''+search_terms[i])

            if fields[i]=="done" or fields[i]=="lokið":
                #search for unfinished (0) and there is not mark for done in data - include in results
                if search_terms[i] == "0" and line[indices[i]]=="":
                    pass
                elif str(line[indices[i]])!=search_terms[i]:
                    return False
            else:
                if len(line)<=indices[i] or not re_comp.search(str(line[indices[i]])):
                    return False
        return True

    def get_next(self):
        return self.results.get()

class Sentence():

    def __init__(self, data, nr, is_sentence):
        self.parts = self.split_sentence(data)
        self.nr = nr
        self.is_sentence = is_sentence


    def get_part(self, index):
        return self.parts[index]

    def get_parts(self):
        return self.parts

    def length(self):
        return len(self.parts)

    #splits in parts while processing data
    def split_sentence(self, sentence):
        parts = []
        tmp = []
        for i in range(0, len(sentence)):

            if i>0 and i%max_len_of_sent==0:
                parts.append(tmp)
                tmp = []
            tmp.append(sentence[i])
        if len(tmp)>0:
            parts.append(tmp)

        return parts



    def get_text(self):
        parts = []
        for part in self.get_parts():
            t=""
            for line in part:
                t+=line[wordform_i]+" "
            parts.append(t)
        return parts

    #splits a setnecne in two
    def split(self, p_index, l_index):

        sents = [[]]
        index = 0
        parts = self.get_parts()
        for i in range(0, len(parts)):
            y = 0
            for line in parts[i]:
                if i==p_index and y == l_index:
                    index+=1
                    sents.append([])
                sents[index].append(line)
                y+=1

        return sents

class Data():

    def __init__(self, path_to_file):
        self.last_saved_time = time.time()
        self.path_to_file = path_to_file
        self.path_to_folder = path_to_file.rsplit("/",1)[0]
        self.filename = path_to_file.rsplit("/",1)[1]
        self.length2 = 0 # how many real sentences
        self.sentences = self.read_data()
        self.length = len(self.sentences) # amount of sentences
        self.curr_part_len = None
        self.index = None
        self.p_index = None
        self.errormarks = []
        self.curr_mark = "" #given value when user pressed a key in mark-widget - possible to use to correct when key is released
        self.go_to_index(0,0)

    def get_curr_part(self):
        return self.sentences[self.index].get_part(self.p_index)

    def get_curr_sentence(self):
        return self.sentences[self.index]

    def is_sentence(self, sentence):

        if len(sentence)==1 and sentence[0][0].startswith("#"):
            return False

        return True

    def read_data(self):
        nr = 0
        #TODO : eyða tómum línum í lokin
        data = []
        f = codecs.open(self.path_to_file, "r")
        text = f.read().strip()
        f.close()
        lines = text.splitlines()
        sentence = []
        #iterate through each line of document
        for line in lines:

            if line.strip()=="":
                #data.append(
                if self.is_sentence(sentence):
                    nr+=1
                    data.append(Sentence(sentence, nr, True))

                else:
                    data.append(Sentence(sentence, None, False))

                sentence = []
            else:
                sentence.append(self.add_empty(line.strip().split(separator)))

        if len(sentence)>0:
            if self.is_sentence(sentence):
                nr+=1
                data.append(Sentence(sentence, nr, True))
            else:
                data.append(Sentence(sentence, None, False))

        self.length2 = nr
        return data

    #adds empty values to list to have all lines the length of max_i
    def add_empty(self, line):

        while len(line)<=max_i:
            line.append("")

        return line

    def next_sentence(self):
        new_index = None
        for i in range(self.index+1,len(self.sentences)):
            if self.sentences[i].is_sentence:
                new_index = i
                break

        if new_index is not None:
            self.index = new_index
            self.curr_sentence = self.sentences[self.index]
            self.p_index = 0
            self.curr_part = self.curr_sentence.get_part(self.p_index)
            self.update_lengths()

    def prev_sentence(self):

        new_index = None
        for i in range(self.index-1,-1, -1):
            if self.sentences[i].is_sentence:
                new_index = i
                break

        if new_index is not None:
            self.index = new_index
            self.curr_sentence = self.sentences[self.index]
            self.p_index = 0
            self.curr_part = self.curr_sentence.get_part(self.p_index)
            self.update_lengths()

    def next_part(self):

        if self.p_index<self.curr_sentence.length()-1:
            self.p_index+=1
            self.curr_part = self.curr_sentence.get_part(self.p_index)
            self.update_lengths()
        else:
            self.next_sentence()

    def prev_part(self):

        if self.p_index>0:
            self.curr_sentence = self.sentences[self.index]
            self.p_index-=1
            self.curr_part = self.curr_sentence.get_part(self.p_index)
            self.update_lengths()
        else:
            self.prev_sentence()

    def go_to_index(self, index, p_index):

        if index<self.length and index>=0:
            self.index = index
            self.p_index = p_index
            self.curr_sentence = self.sentences[self.index]
            self.curr_part = self.sentences[self.index].get_part(self.p_index)
            self.update_lengths()

    def go_to_nr(self, nr):

        index = None
        if nr<self.length and nr>=0:
            for i in range(nr-1, self.length):

                if self.sentences[i].nr is not None and self.sentences[i].nr == nr:
                    index = i
                    self.go_to_index(index, 0)
                    break

    def update_lengths(self):

        self.curr_part_len = len(self.curr_part)

    def validate(self, marks):
        self.errormarks = []
        has_errors = False
        for i in range(0, self.curr_part_len):
            if not tagset.exists(marks[i].get()):
                app.set_error_mark(i)
                self.errormarks.append(marks[i])
                has_errors = True

        return not has_errors

    def split_sentence(self, line_index):

        sentence = self.sentences[self.index]
        sentences = sentence.split(self.p_index, line_index)
        if len(sentences)==2:
            curr_nr = sentence.nr
            #replace current sentence with first part
            self.sentences[self.index]=Sentence(sentences[0], curr_nr, True)
            #inesrt the new sentence
            self.sentences.insert(self.index+1, Sentence(sentences[1], curr_nr+1, True))

            self.length2+=1
            self.length+=1

            for i in range(self.index+2, self.length):
                if self.sentences[i].is_sentence:
                    self.sentences[i].nr+=1

            self.index+=1
            self.curr_sentence = self.sentences[self.index]
            self.p_index = 0
            self.curr_part = self.curr_sentence.get_part(self.p_index)
            self.update_lengths()


    def join_sentences(self, line_index):

        if self.index>0 and self.sentences[self.index-1].is_sentence:
            sentences = [self.sentences[self.index-1], self.sentences[self.index]]
            curr_nr = self.sentences[self.index-1].nr
            data = []
            for sentence in sentences:
                for part in sentence.get_parts():
                    for line in part:
                        data.append(line)

            new_sentence = Sentence(data, curr_nr, True)
            self.sentences[self.index-1] = new_sentence
            del self.sentences[self.index]
            self.length-=1
            self.length2-=1


            for i in range(self.index, self.length):
                if self.sentences[i].is_sentence:
                    self.sentences[i].nr-=1

            self.index-=1
            self.curr_sentence = self.sentences[self.index]
            self.p_index = 0
            self.curr_part = self.curr_sentence.get_part(self.p_index)
            self.update_lengths()
            '''for i in range(0, 4):
                print("##### {}".format(self.sentences[i].nr))
                parts = self.sentences[i].get_parts()
                for part in parts:
                    for line in part:
                        print(line[0])'''


    #changes content of curr_sentence
    def change(self, marks, lemmas, remarks, dones):

        has_changed = False

        if not self.validate(marks):
            print("#### Villa í mörkun:")
            print("Eftirfarandi mörk eru ekki gild:")
            for mark in self.errormarks:
                print(mark.get())

            return False
        else:

            for d, m, l, r, dn in zip(self.curr_part, marks, lemmas, remarks, dones):


                if d[lemma_i] != l.get().strip():
                    has_changed =True
                    d[lemma_i] = l.get().strip()
                if d[tag_i] != m.get().strip():
                    has_changed =True
                    d[tag_i] = m.get().strip()
                if len(d)>remark_i and d[remark_i] != r.get().strip():
                    has_changed =True
                    d[remark_i] = r.get().strip()
                if len(d)>done_i and dn.get()!="":
                    has_changed =True
                    d[done_i] = dn.get()

            #if has_changed:
            #    self.save(".tmp")


            sec_since_saved = time.time()-self.last_saved_time
            if sec_since_saved>5*60:
                print("VISTA...")
                self.save(".tmp")
                self.last_saved_time = time.time()

            return True

    def save(self, extension):

        tmp_file = os.path.join(self.path_to_folder, "__"+self.filename+extension)

        f = open(tmp_file, "w")
        f.truncate()
        f.close()
        with codecs.open(tmp_file, "a", "utf-8") as f:

            for sentence in self.sentences:
                for part in sentence.get_parts():
                    for line in part:
                        f.write("\t".join(str(item) for item in line)+"\n")
                f.write("\n")


        os.rename(tmp_file, self.path_to_file+extension)

    '''def search(self, field, search_term, curr_index):

        #TODO: búa til lista með öllum fundum setningum og línum esm hægt er að ferðast um
        index = None
        re_comp = re.compile(search_term)
        if field not in ["tag","remark","wordform","mark","ath","orðmynd"]:
            errorMsg = "Aðeins er hægt að leita eftir mark, remark eða wordform"
            app.writeMsg(errorMsg, "red")
            return None, None

        else:

            results = {}
            results_keys = []
            if field=="tag" or field=="mark":
                index = tag_i
            elif field=="wordform" or field=="orðmynd":
                index = wordform_i
            elif field=="remark" or field=="ath":
                index = remark_i


            for i in range(self.index, self.length):


                for j in range(0, len(self.sentences[i])):

                    for k in range(0, len(self.sentences[i][j])):
                        line = self.sentences[i][j][k]
                        if len(line)>index and re_comp.search(line[index]):
                            if i in results_keys:
                                results[i].append(k)
                            else:
                                results_keys.append(i)
                                results[i] = [k]


            return results, results_keys

        return []'''

    def get_sentence_as_string(self):

        sent = self.get_curr_sentence()
        return sent.get_text()

class Tagset():

    def __init__(self, filename_set, filename_words, filename_valid_tags):

        self.tags = self.read_tagset(filename_set)
        self.words_and_tags = self.read_words_and_tags(filename_words)
        self.valid_tags = []
        self.valid_letters = []
        self.valid_tags_order = []


        self.read_valid_tags(filename_valid_tags)
        self.set_valid_letters()


    def read_valid_tags(self, filename):

        f = open(filename,"r")
        text = f.read()
        f.close()

        self.valid_tags = eval(text) #convert text to dict

        if "order" in self.valid_tags:
            self.valid_tags_order = self.valid_tags['order']
        else:
            self.valid_tags_order = list(self.valid_tags)

    def read_tagset(self, filename):

        data = set()
        f = codecs.open(filename, "r")
        lines = f.readlines()
        f.close()

        for line in lines:

            if line.strip()!="":
                data.add(line.strip())

        return sorted(data)

    def read_words_and_tags(self, filename):

        data = {}
        f = codecs.open(filename, "r")
        lines = f.readlines()
        f.close()

        for line in lines:
            splt = line.split("\t")
            key = splt[0]
            marks = splt[1]
            data[key] = []
            marks_splt = marks.split("#")
            for mark in marks_splt:
                #TODO: sorta mörk eftir tíðni
                splt = mark.split(" ")
                data[key].append(mark)

        return data

    #returns a list with all letters that appear in tagset
    def set_valid_letters(self):

        self.valid_letters = []
        for key in self.valid_tags:
            if key not in self.valid_letters:
                self.valid_letters.append(key)


            for set in self.valid_tags[key][1]:
                for l in set:
                    if l not in self.valid_letters:
                        self.valid_letters.append(l)


    def exists(self, tag):

        return tag in self.tags

    #Checks if combination of letter is valid (is found in tagset)
    def is_possible_mark(self, string):

        red = self.tags
        for index in range(0, len(string)):
            for tag in red:
                red = [idx for idx in red if len(idx)>index and idx[index] == string[index]]

        if len(red)>0:
            return True

        return False

    def get_possible_marks(self, word, mark_chosen, remark):
        data = []

        for mark in self.words_and_tags[word]:
            data.append(mark.split(" ")[0])

        if mark_chosen not in data:
            data.append(mark_chosen+"*")

        if remark in possible_marks_add:
            for mark in possible_marks_add[remark]:
                if mark not in data:
                    data.append(mark+"*")

        return data

    def is_valid_letter(self, letter):

        return letter in self.valid_letters

    def get_values_by_index(self, index, mark):
        values = []
        if index>0:
            first_letter = mark[0]

            if index<len(self.valid_tags[first_letter][1])+1:

                for i in range(0,len(self.valid_tags[first_letter][1][index-1])):
                    letter = self.valid_tags[first_letter][1][index-1][i]
                    descr = self.valid_tags[first_letter][2][index-1][i]
                    possible_beginning = mark[:index]+letter
                    if self.is_possible_mark(possible_beginning):
                        values.append("{}: {}".format(letter,descr))
        else:
            for letter in self.valid_tags_order:
                values.append("{}: {}".format(letter,self.valid_tags[letter][0]))

        return values

    def validate_part_or_mark(self, mark):

        try:

            if mark[0] not in self.valid_tags:
                return 0

            for i in range(1,len(mark)):
                #mark is too long

                if i>len(self.valid_tags[mark[0]][1]):
                    return len(self.valid_tags[mark[0]][1])+1
                #letter is not valid in this position
                if mark[i] not in self.valid_tags[mark[0]][1][i-1]:
                    #print(mark[i], (i-1))
                    return i

            return len(mark)

        except KeyError as e:
            print("VILLA1")
            print(e)
            print(valid_tags[mark[0]])
            return 0
        except IndexError as e:
            print("VILLA2")
            print(e)
            print(valid_tags[mark[0]])
            return 0



    def print_tagset(self):

        for tag in self.tags:
            print(tag)

# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class Window(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, width, height, master=None):

        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        #reference to the master widget, which is the tk window
        self.master = master

        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window(width, height)

    #Creation of init_window
    def init_window(self, width, height):

        self.PADY = 0 # padding after and before widgets
        self.width = width
        self.height = height
        self.sentence_index = 0
        self.sentence = []
        self.wordforms = []
        self.marks = []
        self.marks_tkvar = []
        self.btn_tags2 = []
        self.tags2_var = []
        self.lemmas = []
        self.remarks = []
        self.check_done = []
        self.var_done = []
        self.btn_modes = []
        self.modes_var = []
        #self.other1 = []
        self.curr_row = 0
        self.curr_col = 0
        self.dropdown_dict = {}
        self.current_marks = [] #current mark selected
        self.active_index = -1 # what line (word) is active
        self.end_index = 0 # how many items (words) are in current window
        self.search_results = {}
        self.search_results_keys = []
        self.search_results_index = 0
        self.initial_dir = "/home/"
        self.goto_locked = False

        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # changing the title of our master widget
        self.master.title("Markari")
        self.grid(sticky="news")

        defaultbg = self.master.cget('bg')

        # allowing the widget to take the full space of the root window
        #self.pack(fill=BOTH, expand=1)
        #self.grid(row=0, column=0)

        # creating a menu instance

        self.frame_nav = Frame(self.master)
        self.frame_nav.grid(row=0, column=0)

        self.frame_search = Frame(self.master)
        self.frame_search.grid(row=1, column=0)

        #self.master.bind("<Button-1>", self.mark_loses_focus)

        menu = Menu(self.master)
        self.master.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Opna  Ctrl-o", command=self.open_file)
        file.add_command(label="Vista  Ctrl-s", command=self.client_save)
        file.add_command(label="Vista og loka  Ctrl-q", command=self.client_save_exit)
        file.add_command(label="Loka án vistunar  Ctrl-x", command=self.client_exit)

        #added "file" to our menu
        menu.add_cascade(label="Skrá", menu=file)

        # create the file object)
        help = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        #edit.add_command(label="Show Img", command=self.showImg)
        help.add_command(label="Leiðbeiningar", command=self.instructions)

        #added "file" to our menu
        menu.add_cascade(label="Hjálp", menu=help)

        button_prev = Button(self.frame_nav, text = "Fyrri setning", command=self.prev_sentence)
        #button_prev.grid(row=0, column=0, pady = 8)
        button_prev.pack(side=LEFT)

        self.label_sent_nr = Label(self.frame_nav, text="0/0")
        self.label_sent_nr.pack(side=LEFT)

        button_next = Button(self.frame_nav, text = "Næsta setning", command=self.next_sentence)
        #button_next.grid(row=0, column=2, pady = 8)
        button_next.pack(side=LEFT)

        label_goto = Label(self.frame_nav, text = "Setn. nr")
        #label_goto.grid(row=0, column=3, pady = 8)
        label_goto.pack(side=LEFT)

        self.text_goto = Entry(self.frame_nav)
        #self.text_goto.grid(row=0, column=4, pady = 8)
        self.text_goto.pack(side=LEFT)
        self.text_goto.bind("<Return>", self.entered_goto)
        self.text_goto.bind("<KP_Enter>", self.entered_goto)

        #bt_show_sent = Button(self.frame_nav, text="Sjá setningu", command=data.show_sentence)
        #bt_show_sent.pack(side=LEFT)


        ####search###

        label_search = Label(self.frame_search, text = "Leita")
        label_search.pack(side=LEFT)

        self.text_search = Entry(self.frame_search)
        self.text_search.pack(side=LEFT)
        #self.text_search.bind("<Return>", self.search_next_)
        self.text_search.bind("<KeyRelease>", self.search_typed)

        button_search_prev = Button(self.frame_search, text = "<", command=self.search_prev)
        button_search_prev.pack(side=LEFT)

        self.label_search_nr = Label(self.frame_search, text="0/0")
        self.label_search_nr.pack(side=LEFT)

        button_search_next = Button(self.frame_search, text = ">", command=self.search_next)
        button_search_next.pack(side=LEFT)

        self.frame_main = Frame(self.master, bg=defaultbg)
        self.frame_main.grid(row=2, column=0)

        frame_main_nav = Frame(self.frame_main, bg=defaultbg)
        frame_main_nav.grid(row=0, column=0, pady=(5, 0), sticky='nw')

        btn_parts_prev = Button(frame_main_nav, text="<", command=self.prev_part)
        btn_parts_prev.pack(side=LEFT)

        self.label_part_nr = Label(frame_main_nav, text="0/0", bg=defaultbg)
        self.label_part_nr.pack(side=LEFT)

        btn_parts_next = Button(frame_main_nav, text=">", command=self.next_part)
        btn_parts_next.pack(side=LEFT)

        self.msgLabel_v = StringVar()
        self.msgLabel = Label(frame_main_nav, textvariable=self.msgLabel_v)
        self.msgLabel.pack(padx=20)


        # Create a frame for the canvas with non-zero row&column weights
        self.frame_canvas = Frame(self.frame_main)
        self.frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky='nw')
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        self.canvas = Canvas(self.frame_canvas)
        self.canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.vsb = Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Create a frame to contain the buttons
        self.frame_buttons = Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.frame_buttons, anchor='nw')

        self.sw_text = Text(sent_window)
        self.sw_text.pack()
        self.sw_text.tag_configure('not_part',
            foreground='#476042')
        self.sw_text.tag_configure('part',
            foreground='#FF0000')

        self.load_widgets()
        if data is not None:
            self.master.winfo_toplevel().title("Markari: "+data.path_to_file)
            self.go_to_sentence(1, [])


        self.listbox = Listbox(self.frame_main)
        self.listbox.selection = -1 #indicates what is selected
        self.listbox.bind('<<ListboxSelect>>', self.listbox_onselect)

        self.master.bind_all('<Control-s>', self.client_save_)
        self.master.bind_all('<Control-q>', self.client_save_exit_)
        self.master.bind_all('<Control-x>', self.client_exit_)
        self.master.bind_all('<Control-o>', self.open_file_)


        #self.master.bind("<KeyRelease>",self.master_keyrelease)

    def open_file_(self, e):
        self.open_file()

    def open_file(self):

        self.filename =  filedialog.askopenfilename(initialdir = self.initial_dir,title = "Veldur skjal",filetypes = (("mörkun","*.correct"),("textaskjöl","*.txt"),("all files","*.*")))
        try:
            self.initial_dir = self.filename.rsplit("/",1)[0]
            open_file(self.filename)
            self.master.winfo_toplevel().title("Markari: "+data.path_to_file)
            self.go_to_sentence(1, [])
        except IndexError:
            pass

    def instructions(self):

        webbrowser.open("hjalp.html")

    #changes color of text to indicate error
    def set_error_mark(self, i):

        self.marks[i].config(bg = "red")

    def writeMsg(self, msg, color):

        self.msgLabel_v.set(msg)
        self.msgLabel.config(foreground=color)

    def clearMsg(self):

        self.msgLabel_v.set("")
        self.msgLabel.config(foreground="black")

    def remove_sentence(self):

        a = datetime.datetime.now()

        for i in range(0,len(self.sentence)):

            self.wordforms[i].grid_forget()
            self.marks[i].grid_forget()
            self.btn_modes[i].grid_forget()
            self.lemmas[i].grid_forget()
            self.remarks[i].grid_forget()
            #self.other1[i].grid_forget()

    def load_widgets(self):

        for i in range(0, max_len_of_sent):
            row = i
            column = 0
            self.wordforms.append(Entry(self.frame_buttons))
            self.wordforms[i].grid(row=row, column=column, pady=self.PADY, padx=5)
            column+=1

            self.marks.append(Entry(self.frame_buttons))
            self.marks[i].name = i
            self.marks[i].grid(row=row, column=column)
            column+=1

            self.modes_var.append(StringVar())
            self.modes_var[i].set("f")
            #self.modes_var.append(StringVar())
            action = partial(self.change_mode, i)
            self.btn_modes.append(Button(self.frame_buttons, textvariable=self.modes_var[i], command=action))
            self.btn_modes[i].name = i
            self.btn_modes[i].grid(row=row, column=column , pady=self.PADY, padx=5 )
            column+=1


            for index in range(0, len(taggers_i)):
                self.tags2_var.append([])
                self.tags2_var[index].append(StringVar())
                self.tags2_var[index][i].set("")

                action = partial(self.btn_set_tag, i, index)
                self.btn_tags2.append([])
                self.btn_tags2[index].append(Button(self.frame_buttons, textvariable=self.tags2_var[index][i], width=5, command=action))
                self.btn_tags2[index][i].name = i
                self.btn_tags2[index][i].grid(row=row, column=column , pady=self.PADY, padx=5 )
                column+=1

            self.lemmas.append(Entry(self.frame_buttons))
            self.lemmas[i].bind("<FocusIn>", self.mark_loses_focus)
            if show_lemmas:
                self.lemmas[i].grid(row=row, column=column, pady=self.PADY, padx=5)
                column+=1
            self.lemmas[i].bind("<KeyRelease>", self.correct_accented)

            self.remarks.append(Entry(self.frame_buttons))
            self.remarks[i].bind("<FocusIn>", self.mark_loses_focus)
            self.remarks[i].grid(row=row, column=column, pady=self.PADY, padx=5)
            column+=1
            self.remarks[i].bind("<KeyRelease>", self.correct_accented)

            v = IntVar()
            self.var_done.append(IntVar())
            self.check_done.append(Checkbutton(self.frame_buttons, variable=self.var_done[i]))
            self.check_done[i].grid(row=row, column=column)
            column+=1

            self.marks[i].bind("<BackSpace>", self.key_backspace)
            self.marks[i].bind("<KeyRelease>", self.key_release)
            self.marks[i].bind("<KeyPress>", self.key_press)
            self.marks[i].bind("<ButtonRelease>", self.mark_widget_clicked)
            self.marks[i].bind("<Control-a>", self.change_mode_)
            self.marks[i].bind("<Control-F1>", self.split_sentence)
            self.marks[i].bind("<Control-F2>", self.join_sentences)
            self.marks[i].bind("<FocusOut>", self.mark_loses_focus)

    def split_sentence(self, e):
        print("split")
        data.split_sentence(self.active_index)

        if search.results is not None and search.results.length>0:
            data.prev_sentence()
            search.clear()
            self.search_next()
        self.go_to_sentence(0, [])

    def join_sentences(self, e):
        if(data.index>0 and data.p_index==0 and self.active_index==0):
            data.join_sentences(self.active_index)
            search.clear()
            self.search_next()
        self.go_to_sentence(0, [])


    def load_sentence(self, line_cursor, line_marked):
        #write in sentence_window
        if Toplevel.winfo_exists(sent_window):
            self.sw_text.delete('1.0', END)
            parts = data.get_sentence_as_string()


            for i in range(0, len(parts)):
                if i==data.p_index:
                    self.sw_text.insert(END, parts[i],'part')
                else:
                    self.sw_text.insert(END, parts[i],'not_part')

        self.sentence_part = data.curr_part

        self.dropdown_dict = {}
        self.modes = []
        #self.modes_var = []
        self.current_marks = []
        self.canvas_height = 0
        self.menu_is_open = False

        self.end_index = len(self.sentence_part)-1
        #if the sentence is longer than the amount of rows, new ones have to been added
        #not necessary if all are loaded in the beginning
        '''if len(self.wordforms)< self.end_index:
            print("villa, á ekki að fara hingað!!")
            exit()

            for i in range(len(self.wordforms), len(self.sentence_part)):
                row = i
                self.wordforms.append(Entry(self.frame_buttons))
                self.wordforms[i].grid(row=row, column=0, pady=5, padx=5)
                self.wordforms[i].config(disabledforeground="black",disabledbackground="white")

                self.marks.append(Entry(self.frame_buttons))
                self.marks[i].name = i
                self.marks[i].grid(row=row, column=1)


                self.modes_var.append(StringVar())

                self.lemmas.append(Entry(self.frame_buttons))
                self.lemmas[i].bind("<FocusIn>", self.mark_loses_focus)
                self.lemmas[i].grid(row=row, column=3, pady=5, padx=5)

                self.remarks.append(Entry(self.frame_buttons))
                self.remarks[i].bind("<FocusIn>", self.mark_loses_focus)
                self.remarks[i].grid(row=row, column=4, pady=5, padx=5)

                self.marks[i].bind("<BackSpace>", self.key_backspace)
                self.marks[i].bind("<KeyRelease>", self.key_release)
                self.marks[i].bind("<ButtonRelease>", self.mark_widget_clicked)'''

        #change value and status of active widgets
        for i in range(0,len(self.sentence_part)):
            row = i

            try:

                self.current_marks.append(self.sentence_part[i][1])

                self.wordforms[i].config(state=NORMAL)
                self.wordforms[i].delete(0,END)
                self.wordforms[i].insert(0, self.sentence_part[i][0])
                self.wordforms[i].config(state=DISABLED)

                if i in line_marked:
                    self.wordforms[i].config(disabledforeground="black",disabledbackground="green yellow")
                else:
                    self.wordforms[i].config(disabledforeground="black",disabledbackground="white")


                self.marks[i].config(state=["normal"])
                self.marks[i].delete(0,END)
                self.marks[i].insert(0, self.sentence_part[i][1])
                self.marks[i].config(state=["readonly"])
                self.marks[i].config(disabledforeground="black",disabledbackground="gray")
                self.marks[i].config(fg="black",bg="white")

                index = 0
                for tagger_i in taggers_i:
                    if self.sentence_part[i][tagger_i]!="":
                        self.tags2_var[index][i].set(self.sentence_part[i][tagger_i])
                        self.btn_tags2[index][i].name = i
                    else:
                        self.btn_tags2[index][i].config(state="disabled")
                    index+=1

                action = partial(self.change_mode, i)

                self.btn_modes[i].config(state=NORMAL)
                self.modes_var[i].set("f")
                self.btn_modes[i].name = i


                self.lemmas[i].config(state=NORMAL)
                self.lemmas[i].delete(0,END)
                self.lemmas[i].insert(0, self.sentence_part[i][2])


                self.remarks[i].config(state=NORMAL)
                self.remarks[i].delete(0,END)
                if len(self.sentence_part[i])>3:
                    self.remarks[i].insert(0, self.sentence_part[i][3])

                self.check_done[i].config(state="normal")
                if len(self.sentence_part[i])>done_i:
                    try:
                        if self.sentence_part[i][done_i]=="":
                            self.var_done[i].set(0)
                        elif int(self.sentence_part[i][done_i])==0:
                            self.var_done[i].set(0)
                        elif int(self.sentence_part[i][done_i])==1:
                            self.var_done[i].set(1)
                        else:
                            print("VILLA: Gildi má aðein vera 0 eða 1 í dálki {}".format(done_i+1))
                    except ValueError as err:

                        print(err)
                        print("VILLA: Gildi fyrir lokið/ólokið má aðeins vera 0 eða 1 (eða tómt)")
                        exit()
                else:
                    self.var_done[i].set(0)


                self.curr_row = i+1
                self.modes.append("f")
            except IndexError as err:
                print("VILLA IE1")
                print(err)
                print("index: {}".format(i))

        #make rest of widget unactive

        for i in range(len(self.sentence_part),len(self.wordforms)):

            self.wordforms[i].config(state="normal")
            self.wordforms[i].delete(0,END)
            self.wordforms[i].config(state="readonly")
            self.marks[i].config(state="normal")
            self.marks[i].delete(0,END)
            self.marks[i].config(state="readonly")

            self.lemmas[i].delete(0,END)
            self.lemmas[i].config(state="readonly")

            self.remarks[i].delete(0,END)
            self.remarks[i].config(state="readonly")
            self.check_done[i].config(state="disabled")

            self.btn_modes[i].config(state="disabled")
            for index in range(0, len(taggers_i)):
                self.btn_tags2[index][i].config(state="disabled")
            #self.var_done[i].

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes'''
        self.frame_buttons.update_idletasks()
        height = self.wordforms[len(self.wordforms)-1].winfo_rooty()-self.wordforms[0].winfo_rooty()+self.wordforms[0].winfo_height()+10

        if height > self.height:
            height = self.height

        # Resize the canvas frame
        self.frame_canvas.config(width=self.width-10,
                            height=self.height-100)

        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    #sets focus on widget
    def set_focus(self, widget):

        widget.focus()
        widget.selection_range(0, END)
        widget.icursor(0)


    #set focus on next marks-widget
    def set_focus_marks_next(self):

        index = None
        rs = search.get_by_indices(data.index, data.p_index)
        if len(rs)>0:
            for i in rs:
                if i > self.active_index:

                    index = i
                    break
            if index is None:

                if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
                    search.next(None)
                    self.search_go_to_next()
                    return
            else:
                self.active_index = index
        else:
            if self.active_index < self.end_index:
                self.active_index+=1
            else:
                self.next_part()


        self.set_focus(self.marks[self.active_index])
        self.listbox.selection = -1

    #set focus on prev marks-widget
    def set_focus_marks_prev(self):

        if self.active_index>0:
            self.active_index-=1
            self.set_focus(self.marks[self.active_index])
            self.listbox.selection = -1

    def btn_set_tag(self, line_i, btn_i):
        self.active_index = line_i
        if self.modes_var[self.active_index].get()=="f":
            self.marks[self.active_index].config(state=NORMAL)
        self.marks[self.active_index].delete(0,END)
        self.marks[self.active_index].insert(0, self.tags2_var[btn_i][self.active_index].get())

        if self.modes_var[self.active_index].get()=="f":
            self.marks[self.active_index].config(state="readonly")

        self.var_done[self.active_index].set(1)

    def get_mode(self):
        return self.modes_var[self.active_index].get()

    def listbox_is_open(self):

        if self.listbox.winfo_ismapped()==0:
            return False
        else:
            return True


    def mark_widget_clicked(self, e):

        self.active_index = e.widget.name
        if self.get_mode() == "f":

            if self.listbox_is_open():
                self.remove_listbox()
            else:
                self.load_listbox(e.widget, 0)

        else:
            if self.active_index != e.widget.name:

                e.widget.selection_range(0, END)
                e.widget.icursor(0)


            index = e.widget.index(INSERT)
            self.load_listbox(e.widget, index)


    def mark_loses_focus(self,e):
        self.remove_listbox()


    def change_mode_(self, e):

        self.change_mode(e.widget.name)

    def change_mode(self, index):

        curr = self.modes_var[index].get()
        self.remove_listbox()
        if curr=="f":
            #self.set_mode("combobox", index)
            self.modes_var[index].set("r")
            self.marks[index].focus
            self.marks[index].config(state="normal")
        else:
            self.modes_var[index].set("f")
            self.marks[index].config(state="readonly")

            #self.set_mode("optionmenu", index)


    def set_mode(self, type, index):
        if type == "optionmenu":
            pass
            #row = self.marks[index].grid_info()['row']
            #self.marks[index].grid_forget()
        elif type == "combobox":

            self.marks[index].set(self.current_marks[index])
            self.marks[index].grid(row=row, column=1)



    def mark_full_changed(self, *args, index=None, variable=None):
        try:
            self.current_marks[index] = variable.get()
        except IndexError:
            print("indexError")
            exit()

    #disables backspace defult behaviour
    def key_backspace(self, e):
        return "break"

    def key_backspace2(self, e):
        self.key_release2(e)


    def listbox_onselect(self, e):

        mode = self.modes_var[self.active_index].get()
        if mode=="f":
            try:
                i = e.widget.curselection()[0]
                mark_widget = self.marks[self.active_index]
                mark_selected = e.widget.get(i).replace("*","")
                self.marks[self.active_index].config(state="normal")
                self.marks[self.active_index].delete(0,END)
                self.marks[self.active_index].insert(0,mark_selected)
                self.marks[self.active_index].config(state="readonly")
                self.remove_listbox()
            except IndexError as err:
                print("IndexError 1")
                print(err)
                print(e)
                print(e.widget)




    def insert_letter(self, widget, letter):
        '''new_value = None
        mark = widget.get() #current mark
        index = widget.index(INSERT)

        widget_index = self.active_index
        new_value = None


        if letter in valid_letters:

            first_letter = mark[0]
            index = validate_part_or_mark(mark)

            if len(mark)>1 and index<len(mark):

                new_value = mark[0:index]+mark[index+1:len(mark)]
            else:
                new_value = mark[0:index]
            if new_value is not None:
                self.current_marks[widget_index] = new_value

                widget.delete(0,END)
                widget.insert(0, new_value)'''

    def listbox_next_select(self):

        if self.listbox.selection < self.listbox.size()-1:
            self.listbox.select_clear(self.listbox.selection)
            self.listbox.selection += 1
            self.listbox.select_set(self.listbox.selection)

    def listbox_prev_select(self):

        if self.listbox.selection > 0:

            self.listbox.select_clear(self.listbox.selection)
            self.listbox.selection -= 1
            self.listbox.select_set(self.listbox.selection)

    def key_press(self, e):
        #save current mark
        self.curr_mark = e.widget.get()

    def key_release(self, e):
        print("rele")
        print(e.keycode)
        print(e.char)

        if self.get_mode()=="f":
            #arrows up and down
            if e.keycode == 116: #arrow down
                if self.listbox.winfo_ismapped():#listbox is open
                    self.listbox_next_select()
                else:
                    self.set_focus_marks_next()

            elif e.keycode == 111: #arrow up
                if self.listbox.winfo_ismapped():#listbox is open
                    self.listbox_prev_select()
                else:
                    self.set_focus_marks_prev()

            elif e.keycode == 36: #ENTER

                if self.listbox.selection>=0:

                    text = self.listbox.get(self.listbox.selection).replace("*","")
                    self.marks[self.active_index].config(state=NORMAL)
                    self.marks[self.active_index].delete(0, END)
                    self.marks[self.active_index].insert(0, text)
                    self.marks[self.active_index].config(state="readonly")

                self.var_done[self.active_index].set(1)
                self.remove_listbox()
                self.set_focus_marks_next()


            elif(e.keycode==65): # SPACEBAR
                if self.listbox.winfo_ismapped():
                    self.remove_listbox()
                else:
                    self.load_listbox(self.marks[self.active_index], 0)

            #elif e.char=="s":
            #    self.change_mode(self.active_index)
            else:
                return "break"


        # if mode is s
        else:
            mark = e.widget.get() #current mark
            index = e.widget.index(INSERT)

            widget_index = int(e.widget.name) #index of widget
            new_value = None

            if tagset.is_valid_letter(e.char) :
                first_letter = mark[0]
                new_mark = mark[0:index]+mark[index+1:len(mark)]
                index_to = tagset.validate_part_or_mark(new_mark)
                new_value = new_mark[:index_to]

            else:
                #backspace
                if e.keycode == 22:

                    #delete if cursot is at the end
                    if index==len(mark):
                        new_value = mark[0:len(mark)-1]

                #arrows and Enter
                elif e.keycode in [111,113,114,116,115]:
                    e.widget.icursor(index)

                #Enter keys
                elif e.keycode in[36,104]:
                    self.var_done[self.active_index].set(1)
                    self.remove_listbox()
                    self.set_focus_marks_next()
                #spacebar
                elif e.keycode in[65]:
                    new_value = mark[:index-1]
                    index-=1
                elif e.keycode in[119,37,38]:
                    pass
                    #new_value = self.curr_mark



                else:
                    print("Lykill: {}".format(e.keycode))
                    new_value = mark[:index-1]+mark[index:]
                    index-=1

            if new_value is not None:
                self.current_marks[widget_index] = new_value

                e.widget.delete(0,END)
                e.widget.insert(0, new_value)
                e.widget.icursor(index)

            if e.keycode not in [36, 104]:
                self.load_listbox(e.widget, None)

    def remove_listbox(self):
        self.listbox.delete(0, END)
        self.listbox.place_forget()

    def load_listbox(self,entry, index):

        widget_index = entry.name

        mode = self.modes_var[widget_index].get()
        values = []
        mark = entry.get()
        self.listbox.config(height=0)
        self.listbox.selection = -1 #nothing is selected
        if mode=="f":
            self.listbox.delete(0, END)
            try:
                values = tagset.get_possible_marks(self.wordforms[widget_index].get(), self.sentence_part[widget_index][tag_i],self.sentence_part[widget_index][remark_i])
            except IndexError as e:
                print("IndexError")
                print(len(self.wordforms))
                print(widget_index)
                print(self.sentence_index)
                print(tag_i)
                print(self.sentence)

        else:
            if index is None:
                index = entry.index(INSERT)

            self.listbox.delete(0, END)
            values = []

            values = tagset.get_values_by_index(index, mark)

        for item in values:
            self.listbox.insert(END, item)
        x = entry.winfo_x()
        y = entry.winfo_y() + entry.winfo_height()



        size = self.listbox.size()

        listb_height = size*15
        listb_max_y = y + size*10
        if listb_max_y > self.frame_buttons.winfo_y()+self.frame_buttons.winfo_height():
            self.listbox.place(x=x, y =y-listb_height+14)
        else:
            self.listbox.place(x=x, y =y+40)

    def letter_selected(self, e):


        new_letter = e.widget.get()
        widget_index = int(e.widget.name)
        mark = self.current_marks[widget_index]

        new_value = mark+new_letter
        index = tagset.validate_part_or_mark(new_value)
        new_value = new_value[0:index]
        e.widget.set(new_value)
        self.current_marks[widget_index] = new_value
        self.load_combobox(e.widget)

    #activated when clicked on button "Next ..."
    def next_sentence(self):

        if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
            data.next_sentence()
            self.go_to_sentence(0, [])

    def prev_sentence(self):

        if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
            data.prev_sentence()
            self.go_to_sentence(0, [])

    def next_part(self):

        if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
            data.next_part()
            self.go_to_sentence(0, [])

    def prev_part(self):

        if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
            data.prev_part()
            self.go_to_sentence(0, [])

    def entered_goto(self, e):
        #try:
            nr = int(e.widget.get())
            data.go_to_nr(nr)
            self.go_to_sentence(0, [])
        #except:
        #    pass


    def go_to_sentence(self,line_cursor, line_marked):


        self.label_sent_nr.config(text= str(data.curr_sentence.nr)+"/"+str(data.length2) )
        self.label_part_nr.config(text= str(data.p_index+1)+"/"+str(data.curr_sentence.length()) )

        self.load_sentence(line_cursor, line_marked)
        if len(line_marked)>0:
            self.active_index = line_marked[0]
        else:
            self.active_index = 0

        self.set_focus(self.marks[self.active_index])




    def correct_accented(self, e):

        def to_accented(string):

            if string=='a':
                return 'á'
            elif string=='i':
                return 'í'
            elif string=='e':
                return 'é'
            elif string=='o':
                return 'ó'
            elif string=='u':
                return 'ú'
            elif string=='y':
                return 'ý'
            elif string=='A':
                return 'Á'
            elif string=='E':
                return 'É'
            elif string=='I':
                return 'Í'
            elif string=='O':
                return 'Ó'
            elif string=='U':
                return 'Ú'
            elif string=='Y':
                return 'Ý'
            else:
                return string

        text = e.widget.get()
        match = re.search(r'\´([aeiouyAEIOUY])', text)
        if match:
            text = text.replace(match.group(), to_accented(match.group(1)))
            e.widget.delete(0,END)
            e.widget.insert(0,text)

    def search_typed(self, e):
        self.search_clear(e)
        self.correct_accented(e)

    def search_clear(self, e):
        search.clear()
        self.label_search_nr.config(text= str("0/0") )




    def search_next_(self, e):
        self.search_next()
    #when clicked on > in search box
    def search_next(self):
        self.clearMsg()

        string = self.text_search.get()
        if string.strip()!="":
            #go to next in Search module
            if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
                search.next(string)
                self.search_go_to_next()

    def search_prev(self):

        self.clearMsg()
        string = self.text_search.get()
        if string.strip()!="":
            if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
                search.prev(string)
                self.search_go_to_next()



    def search_go_to_next(self):
        if self.goto_locked:
            pass

        elif search.results is not None and search.results.length>0:

            search_info = search.get_next()
            data.index = search_info[0]
            data.p_index = search_info[1]
            nrs = search_info[2]
            data.go_to_index(data.index, data.p_index)
            self.go_to_sentence(nrs[0],nrs)
            self.label_search_nr.config(text= str(search.results.nr)+"/"+str(search.results.length) )
        else:
            self.load_sentence(0, [])

    def client_exit_(self, e):
        self.client_exit()

    def client_exit(self):
        MsgBox = tk.messagebox.askquestion ('Loka glugga','Ertu viss um að vilja hætta án þess að vista breytingar?',icon = 'warning')
        if MsgBox == 'yes':
            root.destroy()
        else:
            pass



    def client_save_exit_(self, e):
        self.client_save_exit()

    def client_save_exit(self):
        if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
            data.save("")
            root.destroy()

    def client_save_(self, e):
        self.client_save()

    def client_save(self):
        if data.change(self.marks, self.lemmas, self.remarks, self.var_done):
            data.save("")




#creates dict with from a corpus.
#returns dict and a list of all letters uesd in tagset
#TODO: dict á að hafa þrívítt fylki: 0=Heiti flokks, fylki undirflokka (stafur). fylki undirflokka [orð]
'''def create_valid_tags_dict(tagset):
    valid_tags = {}
    valid_letters = []
    for mark in tagset:
        if mark[0] not in valid_tags:
            valid_tags[mark[0]] = []
            if mark[0] not in valid_letters:
                valid_letters.append(mark[0])

        for i in range(1,len(mark)):
            if mark[i] not in valid_letters:
                valid_letters.append(mark[i])

            if len(valid_tags[mark[0]])<i:
                valid_tags[mark[0]].append([])
            if mark[i] not in valid_tags[mark[0]][i-1]:
                valid_tags[mark[0]][i-1].append(mark[i])

    return valid_tags, valid_letters'''



def open_file(filename):
    global data
    data = Data(filename)

try:
    file_name = sys.argv[1]
except:
    file_name = None


separator = "\t"
#file_name = "adjucations.txt"
tagset_file = "markamengi.txt"
words_and_tags_file = "ord_og_mork.txt"
valid_tags_file = "valid_tags.txt"
max_len_of_sent = 25
wordform_i = 0


tag_i = 1
lemma_i = 2
remark_i = 3
taggers_i = []
done_i = 4
show_lemmas = True

max_i = 4

possible_marks_add = {
    'n----s eða e':['n----s','e']
}


data = None
if file_name is not None:
    data = Data(file_name) #class that keeps track of data
    #sents = data.split_sentence( 7)

search = Search() # class that takes care of search
tagset = Tagset(tagset_file, words_and_tags_file, valid_tags_file) #class that validates possible marks etc.

#search.search("ath=.*n----s")
#exit()

# root window created. Here, that would be the only window, but
# you can later have windows within windows.

root = Tk()
width = 900
height = 880


root.geometry(str(width)+"x"+str(height))
sent_window = tk.Toplevel(root)
#creation of an instance
app = Window(width, height, root)





#mainloop
root.mainloop()
