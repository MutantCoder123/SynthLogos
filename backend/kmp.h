#ifndef KMP_H
#define KMP_H
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

// preprocess pattern for lps array
void computeLPS(string pat, int m, int* lps) {
    int len = 0;
    lps[0] = 0;
    int i = 1;
    while(i<m) {
        if(pat[i] == pat[len]) {
            len++;
            lps[i] = len;
            i++;
        }
        else {
            if(len != 0) len = lps[len - 1];
            else {
                lps[i] = 0;
                i++;
            }
        }
    }
}

// search text and return all occurrences
string getSnippet(string text, string pat) {
    string res = "";
    // case insensitive setup
    string lowText = "", lowPat = "";
    for(char c : text) lowText += tolower(c);
    for(char c : pat) lowPat += tolower(c);

    int m = lowPat.length();
    int n = lowText.length();
    if(m == 0) return "";

    int* lps = new int[m];
    computeLPS(lowPat, m, lps);

    int i = 0, j = 0;
    while(i<n) {
        if(lowPat[j] == lowText[i]) {
            j++; i++;
        }
        if(j == m) {
            // match found, get 500 char window
            int startIdx = i - j;
            int start = max(0, startIdx - 500);
            int end = min(n, startIdx + m + 500);
            
            string raw = text.substr(start, end - start);
            
            // sanitize to prevent python bridge crash
            replace(raw.begin(), raw.end(), '|', ' ');
            replace(raw.begin(), raw.end(), '\n', ' ');
            
            res += "..." + raw + "... ";
            j = lps[j - 1];
        }
        else if(i<n && lowPat[j] != lowText[i]) {
            if(j != 0) j = lps[j - 1];
            else i++;
        }
    }
    delete[] lps; // free mem
    if(res.empty()) return "";
    return res;
}
#endif