---
date: 2026-01-01
categories: 
  - "me"
  - "feature"
---

# Welcome to "Insert Coin"

## A Personal Blog

![Generated with Google's Imagen 4](images/Google_AI_Studio_2025-12-28T23_28_41.825Z.png)

After many, MANY years relying on the trusty Wordpress to host my personal site I decided it was high time for a refresher, including a name change.
Googling "Insert Coin" returns several results, so not really original and I struggled to go for another name. But I find this one such a great call-back to the amazing 1980s arcade games which fueled my passion for computers and programming. So ... keeping the name, for now.

Follows a quick summary of what I used to port the existing website from Wordpress to static pages with help from Google's Antigravity IDE.

## Requirements

### 1. Build the whole thing as static html pages.

Wordpress has served me well, but it brings quite some overweight with database processing, a bunch of modules, constant updates, etc. And, frankly, I don't really need any of that considering that I just use this to post something I find interesting, or personal notes once in a blue moon. I also don't care about comments or any forms of interaction so, static will do just fine.

### 2. Template the pages using Markdown

Because ... well ... once a software developer ...

After a quick check of available static site builders, it was clear I wouldn't find anything that would quite fit the purpose so ... time to roll-up the sleeves and build it.

### 3. Use an AI coding agent 

Since we just landed in 2026 and before we reach end-of-times, let's engage the support of a recent AI coding agent IDE to assist.
And by "assist" I mean mostly vibe-coding. The assignment is straightforward enough to leave it up to AI to figure out the code and simply validate the result.

## "Build it and they will come" (TM)

Here's a rundown of the work:

1. Backup the "old" site.
1. Export the entire content of the "old" Wordpress site to XML.
1. Use [wordpress-export-to-markdown](https://github.com/lonekorean/wordpress-export-to-markdown) to do a generic conversion of the XML content into Markdown files.
1. Manually revise each one of the markdown files(!)
1. Select the base for the new site HTML template: ["Editorial" by HTML5 UP](https://html5up.net/editorial)
1. Use [Google Antigravity](https://antigravity.google) to make changes to the base HTML template. Model: Gemini 3 Flash.
1. Iterate with Antigravity to develop a Python script that converts all the markdown files into the corresponding HTML following the given template.
1. Use Antigravity to create a Windows script to FTP all the files to the webhost.

And if you're reading this, then you can see the result.

![Vide Coding Bliss!!!](images/antigravity-recording1.mp4)

## Next steps

Even though the idea is to minimize interactions and keep things static, some form of content search and filtering might be useful. This will be done on the client-side using JavaScript for a future version.

## Conclusion

This was a great experience in "Vibe Coding" even though surpervised. I find it works best when things are taken in small steps and the AI is given fairly simple, objective tasks and some guidance. As opposed to just "build this" and hope for the best.

All the code for the project is available [here](https://github.com/pedrobruno/pedrobruno.net).
