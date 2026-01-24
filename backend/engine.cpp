/**
 * @file engine.cpp
 * @author Indranil Saha
 * @brief Efficient Search Engine for SynthLogos (Headless Mode).
 * @version 1.4
 * @date 24/01/2026
 */
#include<iostream>
#include<fstream>
#include<sstream>
#include<string>
#include<vector>
#include<algorithm>
#include<cmath>
#include<cstring>
#include<dirent.h>
#include "arena.h"
#include "trie.h"
#include "kmp.h" 

using namespace std;

struct Document {
    int id;
    string name;
    string content;
    int num_words;
};

// helper to read text files
string readFile(const string& path) {
    ifstream file(path);
    if(!file.is_open()) {
        cerr << "[ERROR] Could not open file: " << path << endl;
        return "";
    }
    stringstream buf;
    buf << file.rdbuf();
    return buf.str();
}

// ranking on the basis of TF*IDF score
vector<int> ranking(vector<pair<int,double>> &v, vector<Document> &corpus) {
    if(v.empty() || corpus.empty()) return {};
    double doc_feq = (double)v.size();
    for(auto &x : v) {
        double feq = x.second;
        // avoid div by zero
        double num_words = (corpus[x.first - 1].num_words > 0) ? corpus[x.first - 1].num_words : 1;
        double TF = feq / num_words;
        // idf smoothing to fix zero score bug
        double IDF = log10(1 + ((double)corpus.size() / (doc_feq + 1)));
        x.second = TF*IDF;
    }
    sort(v.begin(), v.end(), [](auto &a, auto &b) { return a.second > b.second; }); 
    int cnt = min(10,(int)v.size());
    vector<int> sorted(cnt);
    for(int i=0; i<cnt; i++) sorted[i] = v[i].first;
    return sorted;
}

int main(int argc, char* argv[]) {
    size_t arenaSize = 50 * 1024 * 1024;
    Arena myArena(arenaSize);
    invertedIdx index(&myArena);
    vector<Document> corpus;
    
    // load data automatically
    vector<string> files;
    DIR *dir;
    struct dirent *ent;
    string path = "data/";
    if((dir = opendir(path.c_str())) != NULL) {
        while((ent = readdir(dir)) != NULL) {
            string f_name = ent->d_name;
            if(f_name.length() > 4 && f_name.substr(f_name.length() - 4) == ".txt") {
                files.push_back(path + f_name);
            }
        }
        closedir(dir);
    } else {
        cerr << "[ERR] No 'data' folder found.\n";
        return 1;
    }

    int docId = 1;
    for(const auto& f : files) {
        string c = readFile(f);
        if(c.empty()) continue; 
        corpus.push_back({docId, f, c, 0});
        string word = "";
        int cnt = 0;
        for(char x : c) {
            if(isalnum(x)) word += tolower(x);
            else {
                if(!word.empty()) {
                    index.add(word, docId);
                    word = "";
                    cnt++;
                }
            }
        }
        if(!word.empty()) {
            index.add(word, docId);
            cnt++;
        }
        corpus.back().num_words = cnt;
        docId++;
    }

    // argument parsing (fixed argc check)
    if(argc >= 3 && strcmp(argv[1], "--query") == 0) {
        string q_raw = argv[2];
        string q = "";
        for(char c : q_raw) q += tolower(c);

        vector<pair<int,double>> res = index.search(q);
        if(res.empty()) return 0;
        
        // update scores in place
        vector<int> ranked = ranking(res, corpus);

        for(size_t i = 0; i<ranked.size(); i++) {
            int id = ranked[i];
            string name = corpus[id-1].name;
            string content = corpus[id-1].content;
            double score = res[i].second;
            string snip = getSnippet(content, q_raw); 
            // fallback to lowercase match if strictly case match fails
            if(snip.empty() || snip == "...") snip = getSnippet(content, q);
            
            // sanitation loop to prevent python bridge crash
            for(char &ch : snip) {
                if(ch == '\n' || ch == '\r' || ch == '|') ch = ' ';
            }
            cout << name << "|" << score << "|" << snip << "|" << q_raw << endl;
        }
    }
    else {
        cout << "Usage: ./engine --query \"search_term\"\n";
    }
    return 0;
}