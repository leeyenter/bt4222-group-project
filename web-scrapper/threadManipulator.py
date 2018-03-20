def appendReply(post, threads, quote, postIDs = None):
    # check first if it's been logged before in postIDs
    if postIDs is not None and quote in postIDs:
        parentPost = threads
        for i in postIDs[quote]:
            if type(parentPost) == list:
                parentPost = parentPost[i]
            else:
                parentPost = parentPost['replies'][i]
        postIDs[post["postID"]] = postIDs[quote].copy()
        postIDs[post["postID"]].append(len(parentPost["replies"]))
        parentPost["replies"].append(post)
        return
#    print("not found")
#    for thread in threads:
#        if thread["postID"] == quote:
#            # Found!
#            thread["replies"].append(post)
#            return
#        elif len(thread["replies"]) > 0:
#            appendReply(post, thread["replies"], quote)

def formThreads(posts):
    threads = []

    for post in posts:
        if len(post["quotes"]) == 0:
            # Parent
            threads.append(post)
        else:
            # Look for this thread's parent
            for quote in post["quotes"]:
                appendReply(post, threads, quote)
    
    return threads

def printThread(threads, level):
    for thread in threads:
        print("-"*level, thread["text"][0:50].replace("\n", " "))
        printThread(thread["replies"], level+1)