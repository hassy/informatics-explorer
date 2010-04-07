from django.http import HttpResponse
from django.shortcuts import render_to_response

import time, random, math, os, json
import Stemmer

from utils import *

global_counts = load_json("data/global_counts.json")
sorted_global_counts = sort_by_value(global_counts)
stem_to_terms = load_json("data/stem_to_terms.json")
persons_terms = load_json("data/persons_terms.json")
relevancy_scores = load_json("data/relevancy_scores.json")
persons_memberships = load_json("data/persons_memberships.json")
people_pages = load_json("data/people_pages.json")
topic_words = list(set( slurp("data/topics32.txt").split() ))
buddies = load_json("data/buddies.json")

stemmer = Stemmer.Stemmer("english")

def compute_weights(words):
    """
    Take a list of words, grab their counts in the corpus, normalize the 
    counts to 1-10 scale for display in the cloud.
    """
    
    weights = {}
    counts = {}
    for w in words:
        stemmed_w = stemmer.stemWord(w)
        if stemmed_w in global_counts:
            counts[w] = global_counts[stemmed_w]
    
    counts2 = sort_by_value(counts) # this is a list of tuples now -- (word, count)
    b = counts2[0][1]
    a = counts2[-1][1]
    
    if b - a == 0: b = 2

    for w in counts:
        x = counts[w]
        y = 1 + (x-a)*(10-1)/(b-a)
        weights[w] = y
        
    return weights

def unstem(weighted_words):
    # FIXME:
    result = {}
    for word in weighted_words:
        # Pick a random unstemming
        # FIXME: better heuristic
        if word in stem_to_terms:
            unstemmed_word = random.choice(stem_to_terms[word])
            result[unstemmed_word] = weighted_words[word]
        else:
            result[word] = weighted_words[word]
    return result

def simple_unstem(words):
    result = []
    for word in words:
        if word in stem_to_terms:
            unstemmed_word = random.choice(stem_to_terms[word])
            result.append(unstemmed_word)
        else:
            result.append(word)
    return result


def common_words_for(people):
    """
    Get common words for list of people.
    """
    common_terms = set(persons_terms[people[0]])
    for person in people:
        if persons_terms[person] != []:
            common_terms = common_terms.intersection(set(persons_terms[person]))
    return list(common_terms)

def number_of_people_sharing_term(term, people):
    """
    Return number of people sharing the term.
    """
    n = 0
    for person in people:
        if term in persons_terms[person]:
            n += 1
    return n

def terms_with_count_of(count, term_cloud_counts):
    result = []
    for term in term_cloud_counts:        
        if term_cloud_counts[term] == count:
            result.append(term)
    return result

def top_n_most_relevant_terms(terms_per_person, person):
    """
    Return N most relevant terms for a person.
    """
    s = sort_by_value(relevancy_scores[person])
    terms = [pair[0] for pair in s][0:terms_per_person*2]
    random.shuffle(terms)
    return terms[0:terms_per_person]

### VIEWS HERE:

def home(req):
    return render_to_response("home.html", {})
    
def init_json(req):
    n = random.randint(0, 2)
    if n == 0:
        random.shuffle(topic_words)
        start_words = topic_words[:20]
    elif n == 1:
        start_words = "goal agent information language function model structure algorithm data system tree xml database computer process research translation thread design".split()
    else:
        start_words = "agent ontology knowledge semantics logic calculus performance compiler language learning translation database xml rdf proof tree requirements process user learning text corpus probability design".split()

    weights = compute_weights(start_words)
    
    thejson = json.dumps(weights)
    return HttpResponse(thejson)
    
def app_query(req):
    stemmed_terms = stemmer.stemWords(req.POST["queryWords"].strip().split(", "))
    old_count = int(req.POST["peopleCount"])
    if old_count == 0: old_count = len(persons_terms.keys())
    
    new_group = []
    for person in persons_terms.keys():
        all_found = True
        for term in stemmed_terms:
            if not term in persons_terms[person]:
                all_found = False
                break
        if all_found:
            new_group.append(person)
        all_found = True
    
    if len(new_group) > 5 and int((old_count*0.85)) < len(new_group):
        # FIXME:
        i = int((old_count*0.85))
        new_group = new_group[0:i]
        
    w = 24
    n_total = len(persons_terms.keys())
    n_current = len(new_group)

    if w < n_current: # each term must describe ~N_current/W people
        random.shuffle(new_group)
        group_size = int(math.ceil((1.0*n_current)/w))
        another_term_cloud = []
        pivots = range(0, n_current, group_size)
        for pivot in pivots:
            common_terms = persons_terms[new_group[pivot]]
            for idx in range(pivot+1, pivot+group_size):
                if idx >= len(new_group): break
                common_terms = list(set(persons_terms[new_group[idx]]).intersection(set(common_terms)))
                common_terms_relevancy_scores = {}
                for term in common_terms:
                    common_terms_relevancy_scores[term] = relevancy_scores[new_group[pivot]][term]
                top_cw = [pair[0] for pair in sort_by_value(common_terms_relevancy_scores)][0:group_size*2]
                
            another_term_cloud += top_cw
        another_term_cloud = list(set(another_term_cloud))
        random.shuffle(another_term_cloud)
        another_term_cloud = another_term_cloud[0:w]        
        return HttpResponse(json.dumps({"people": new_group, "weights": unstem(compute_weights(another_term_cloud))}))
    else:
        terms_per_person = int(math.ceil(1.0*w/n_current))
        term_cloud = []
        for person in new_group:
            moar_terms = top_n_most_relevant_terms(terms_per_person, person)
            term_cloud += moar_terms
        
        return HttpResponse(json.dumps({"people": new_group, "weights": unstem(compute_weights(term_cloud))}))
        
def person_details(req, person_id):
    info = {}
    if person_id in persons_memberships:
        info.update(persons_memberships[person_id])
    else:
        info["name"] = ""
        info["url"] = ""
        
    if person_id in people_pages:
        info["homepage_url"] = people_pages[person_id]

    info["photo_url"] = "http://localhost:8000/static/photos/no_photo.png"
    photos = os.listdir("data/photos")
    for p in photos:
        if person_id == p.split(".")[0]:
            info["photo_url"] = "http://localhost:8000/static/photos/"+p
    
    keywords = simple_unstem(top_n_most_relevant_terms(20, person_id))
    info["keywords"] = keywords
    return HttpResponse(json.dumps(info))
    
def buddies_index(req):
    return render_to_response("buddies.html", {})
    
def person_buddies(req, person_id):
    data = {"id": person_id, "name": person_id, "data": {}, "children": []}
    for b in buddies[person_id]:
        if b != person_id:
            data["children"].append({"id": b, "name": b, "data": {}, "children": []})
    return HttpResponse(json.dumps(data))

def static_graph(req):
    return render_to_response("static_graph.html", {})