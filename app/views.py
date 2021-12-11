import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from flask import Flask, request, render_template
from django.http import HttpResponse, HttpResponseRedirect

from predpatt import PredPatt
from predpatt import load_conllu

import subprocess
import json
import requests

import stanza


def dashboard(request): return render(request, 'dashboard.html')


def service(request): return render(request, 'service.html')


def contact(request): return render(request, 'contact.html')


@csrf_exempt
def result(request):
    if request.method == "POST":
        display_type = request.POST.get("display_type")
        text = request.POST.get("input_text")
        if display_type == "perdt":
            stanza.download('fa')  # This downloads the English models for the neural pipeline
            nlp = stanza.Pipeline('fa')  # This sets up a default neural pipeline in English
            doc = nlp(text)
            doc.sentences[0].print_dependencies()
            print(doc.sentences[0])
            for sentence in doc.sentences:
                text = text.strip()
                res = "# text = " + text
                print("# text = " + text)
                res = res.strip() + '\n'
                for word in sentence.words:
                    res = res + str(word.id) + "\t" + str(word.text) + "\t" + str(word.lemma) + "\t" + str(
                        word.pos) + "\t" + str(
                        word.xpos) + "\t" + str(word.feats) + "\t" + str(word.head) + "\t" + str(word.deprel) + "\t" + str(
                        word.start_char) + "\t" + str(word.end_char)
                    print(str(word.id) + "\t" + str(word.lemma) + "\t" + str(word.text) + "\t" + str(word.pos) + "\t" + str(
                        word.xpos) + "\t" + str(word.feats) + "\t" + str(word.head) + "\t" + str(word.deprel) + "\t" + str(
                        word.start_char) + "\t" + str(word.end_char))
                    res = res + '\n'

            print(res)
            print(request.method)
            conll_example = res
            print(conll_example)
            conll_example = [ud_parse for sent_id, ud_parse in load_conllu(conll_example)][0]
            ppatt = PredPatt(conll_example)
            print(" ".join([token.text for token in ppatt.tokens]))
            print(ppatt.pprint(color=True))
            final_res = ppatt.pprint()
            return render(request, 'service.html', {'input_text': text,'conll_text': res, 'output_text': final_res})
        elif display_type == "seraji":
            with open('file.txt','a+', encoding='utf-8') as f:
                f.write(text)
                f_list = list(set(f.readlines()))
                print(f_list)
                for i in f_list:
                    if i == '\n':
                        f_list.remove(i)
                print(f_list)
                f.writelines(f_list)
                f.close()
            bashCommand = """curl -F data=@file.txt -F model=persian -F tokenizer=normalized_spaces -F tagger= -F parser= http://lindat.mff.cuni.cz/services/udpipe/api/process """
            print(bashCommand)
            try:
                send_order = subprocess.check_output(bashCommand.split(), shell=True)
                print(send_order)
            except subprocess.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            print(send_order)
            d = json.loads(send_order)
            print(d)
            print(d["result"])
            conll_example = [ud_parse for sent_id, ud_parse in load_conllu(d["result"])][0]
            print(conll_example.pprint(K=3))
            ppatt = PredPatt(conll_example)
            print(" ".join([token.text for token in ppatt.tokens]))
            print(ppatt.pprint())
            os.remove("file.txt")
            return render(request, 'service.html', {'input_text': text, 'conll_text': d["result"], 'output_text': ppatt.pprint()})
    else:
        return render(request, 'service.html', {'input_text': "", 'output_text': ''})

