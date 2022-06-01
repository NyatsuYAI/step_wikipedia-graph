from asyncio.windows_events import NULL
from calendar import c
from distutils.command import check, clean
from genericpath import exists
from multiprocessing import parent_process
from typing import Container
import copy
import sys


def data_transfer(stack_or_que, index_from_adress_to_name):
    res_list = []
    for adress in stack_or_que:
        res_list.append(index_from_adress_to_name[adress])
    return res_list


def get_keys_from_value(dict, val):
    return [k for k, v in dict.items() if v == val]


def dfs_searcher(
    pages,
    links,
    target_word,
    now_tracking,
    root_link,
    min_tracking_index,
    tracking_review,
):
    parent_node = root_link
    now_tracking.append(parent_node)

    # print(
    #     f"now root is {pages[parent_node]},now traking is {data_transfer(now_tracking,pages)}"
    # )
    tracking_review.append(now_tracking)

    # check target word or not

    if pages[parent_node] == target_word:
        length = len(now_tracking)
        tracking_list = copy.copy(now_tracking)
        min_tracking_index[length] = tracking_list
        # print(f"find target word {data_transfer(now_tracking,pages)}")
        now_tracking.remove(parent_node)
        return min_tracking_index

    # stopper setting
    # if links and pages is large file
    # use this stopper

    if len(min_tracking_index) > 1:
        # Determine the number of answers
        now_tracking.remove(parent_node)
        return min_tracking_index
    elif len(now_tracking) > 5:
        # Countermeasures against maximum recursion depth exceeded
        now_tracking.remove(parent_node)
        return min_tracking_index

    # check leef

    if parent_node not in links:
        # print(f"this is leef")
        now_tracking.remove(parent_node)
        return min_tracking_index
    else:
        childen_nodes = links[parent_node]

    for child_node in childen_nodes:
        if child_node not in now_tracking and child_node is not parent_node:
            min_tracking_index = dfs_searcher(
                pages,
                links,
                target_word,
                now_tracking,
                child_node,
                min_tracking_index,
                tracking_review,
            )

        else:
            pass
    now_tracking.remove(parent_node)

    return min_tracking_index


def bfs_searcher(pages, links, target_word, root_link, tracking_index):

    bfs_que = [root_link]

    tracking_index[root_link] = [root_link]
    already_tracking = set()
    while bfs_que != []:
        # print(bfs_que)
        parent_node = bfs_que[0]
        bfs_que.remove(parent_node)
        already_tracking.add(parent_node)
        if parent_node not in links:
            already_tracking.add(parent_node)
        else:
            link_list = links[parent_node]
            for child_node in link_list:
                if child_node not in already_tracking:
                    now_tracking = copy.copy(tracking_index[parent_node])
                    now_tracking.append(child_node)
                    tracking_index[child_node] = now_tracking
                    # print(f"now traking {data_transfer(now_tracking,pages)}")
                    if pages[child_node] == target_word:
                        return tracking_index[child_node]
                    else:
                        already_tracking.add(child_node)
                        bfs_que.append(child_node)

    return []


def main():
    pages = {}
    links = {}

    with open("data/pages.txt", encoding="utf-8") as f:
        for data in f.read().splitlines():
            page = data.split("\t")
            # page[0]: id, page[1]: title
            pages[page[0]] = page[1]

    with open("data/links.txt") as f:
        for data in f.read().splitlines():
            link = data.split("\t")
            # link[0]: id (from), links[1]: id (to)
            if link[0] in links:
                links[link[0]].add(link[1])
            else:
                links[link[0]] = {link[1]}

    ## target input

    # print(pages.values())
    print("please type root word >", end="")
    root = input()

    if root not in pages.values():
        print("Word does not exist. Choose from the list.")
        main()
        exit()

    print("please type search word >", end="")
    target = input()

    if target not in pages.values():
        print("Word does not exist. Choose from the list.")
        main()
        exit()
    elif target == root:
        print("you already exist here! Choose other words from the list")
        main()
        exit()

    ### dfs & bfs

    print("-----dfs start-----")

    root_link = get_keys_from_value(pages, root)
    try:
        link_tracks = []
        ans = {}
        tracking_review = []
        answer = dfs_searcher(
            pages, links, target, link_tracks, root_link[0], ans, tracking_review
        )
        if answer == {}:
            print("sorry we cant find")
        else:
            answer_sorted = sorted(answer.items(), key=lambda x: x[0])
            print(answer_sorted[0])
            print(data_transfer(answer_sorted[0][1], pages))
            print(f"all answer is {answer_sorted}")

        with open("./review_dfs.txt", "w", encoding="utf-8") as f:
            for data in tracking_review:

                f.write("%s\n" % data_transfer(data, pages))
    except AssertionError as e:
        print(e)

    print("-----dfs finish-----")

    print("-----bfs start-----")

    tracking_index = {}
    answer = bfs_searcher(pages, links, target, root_link[0], tracking_index)
    if answer == []:
        print("sorry we cant find")
    else:
        print(answer)
        print(data_transfer(answer, pages))

    with open("./review_bfs.txt", "w", encoding="utf-8") as f:
        for keys in tracking_index:
            data = tracking_index[keys]
            f.write("%s\n" % data_transfer(data, pages))

    print("-----bfs finish-----")

    for k, v in pages.items():
        if v == target:
            print(target, k)


if __name__ == "__main__":
    main()
