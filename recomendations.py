from math import sqrt

# dictionary of movie critics and their rating of a smal set of movies 

critics = {'Lisa Rose' : {'Lady in the water' : 2.5, 'Snakes on a Plane' : 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupress': 2.5, 'The Night Listener': 3.0}, 
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck' : 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5},
           'Micheal Philips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, 'Superman Returns': 3.5, 'The Night Listener': 4.0}, 
          'Claudia Puig' : {'Snakes on a Plane': 3.5, 'Just my Luck': 3.0, 'The Night Listener': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 2.5},
          'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 2.0},
          'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
          'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


#returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    #Get the list of shared_items 
    si = {}
    for items in prefs[person1]:
        if items in prefs[person2]:
            si[items] = 1
    
    #if they have no rating in common, return 0 
    if len(si) == 0:  return 0 
    
    #Add up the squares of all the differences 
    sum_of_squares = sum ([pow(prefs[person1][item] - prefs[person2][item], 2) 
                           for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1+sum_of_squares)

#Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    #Get the list of mutually rated items 
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1
    
    #find the number of elements 
    n = len(si)
    
    #if they have no ratings in common, return 0
    if n == 0: return 0
    
    #Add up all the preferences 
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    
    #sum up the squares 
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    
    #sum up the products 
    pSum = sum([prefs[p1][it]* prefs[p2][it] for it in si])
    
    #calculate the pearscon score 
    num = pSum - (sum1*sum2/n)
    den = sqrt((sum1Sq- pow(sum1,2)/n) * (sum2Sq - pow(sum2,2)/n))
    
    if den == 0: return 0
    
    r = num/den 
    
    return r

# Returns the best matches for person from the prefs dictionary 
# number of results and similarity function are optional params 

def topMatches (prefs, person, n = 5, similarity = sim_pearson):
    scores = [(similarity(prefs, person, other), other)
                for other in prefs if other != person]
    
    #sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]

#Get recommendations for a person by using a weighted average 
# of evvery other user's ranking
def getRecommendations(prefs, person, similarity = sim_pearson):
    totals = {}
    simSums = {}
    
    for other in prefs:
        # don't compare me to myself 
        if other == person: continue
        sim = similarity(prefs, person, other)
        
        #ignore scores of zero or lower
        if sim <= 0: continue 
        for item in prefs[other]:
                
            #only score movies I haven't seen yet 
            if item not in prefs[person] or prefs[person][item] == 0:
                #Similarity * score 
                totals.setdefault(item,0)
                totals[item] += prefs[other][item] * sim
                #sum of similarities 
                simSums.setdefault(item, 0)
                simSums[item] += sim 
            
    # create the normalized list 
    rankings = [(total/simSums[item], item) for item,total in totals.items()]
        
    #Return the sorted list 
    rankings.sort()
    rankings.reverse()
    return rankings

#transformation to something like people would have read that book also read
# these book 

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            
            #Flip item and person 
            result[item][person] = prefs[person][item]
    return result

def calclateSimilarItems(prefs, n=10):
    #Create a dictionary of items showing which other items 
    #they are most similar to 
    result = {}
    
    #invert the preference matrix to be item-centric 
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs: 
        #status updates for large datasets 
        c+=1
        #if c%100 == 0: print "%d / %d" %(c, len(itemPrefs))
        #Find the most similar items to this one. 
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result 

def getRecommendedItems (prefs, itemMatch, user):
    userRatings=prefs[user]
    scores = {}
    totalSim = {}
    
    #Loop over items rated by this user 
    for (item, rating) in userRatings.items():
        
        #Loop over items similar to this one 
        for (similarity,item2) in itemMatch[item]:
            
            #Ignore if this user has already rated this item
            if item2 in userRatings : continue
                
            #Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2] += similarity*rating 
            
            #sum of all the similarities 
            totalSim.setdefault(item2, 0)
            totalSim[item2]+=similarity 
            
    #divide each total score by total wieighting to get an 
    #average 
    
    rankings = [(score/totalSim[item], item) for item,score in scores.items()]
    
    #Return the rankings from highest to lowest 
    rankings.sort()
    rankings.reverse()
    return rankings 