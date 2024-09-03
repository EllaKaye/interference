## About the game and name

This is a patience (or solitaire) game, 
where a deck of cards is shuffled and dealt into four rows of thirteen cards.
The Aces are then removed, leaving spaces. 
The aim is to sort each row into ascending order, from 2 to King, ending with a space, one row per suit, 
by moving cards into spaces, one at a time, according to the rules. 
See the [Instructions](instructions.md) page for full details on how to play.

I learnt this patience from my grandparents when I was young. 
In my family, we know it as "interference", 
because whenever anybody sits down to play, 
someone else comes and stands over their shoulder and interferes by suggesting what the next move should be.

I couldn't find any information about a patience called "interference"
and finally discovered (as I was writing this page) that it is actually known as <a href="https://en.wikipedia.org/wiki/Gaps" target="_blank">Gaps</a>. 
That said, to me (and in honour of my grandpartents) it's still "interference" and
I'm sticking with that as the name of the game as I've built it here.

## About the development history

I first learnt to code back in 2013 by taking an "Introduction to Programming" online course which taught Python by building simple games.
After the course, I wanted to challenge myself and so I made v1 of Interference, using the CodeSkultpur platform and the simple package (as we'd used in the course). It's still available to <a href="https://py2.codeskulptor.org/#user51_AaJ8ZQvnxh3PPb7.py" target="_blank">play</a>. The game is far more complex than anything we built during the course. It took me weeks to figure out the logic and the corresponding code and, at the time, I was really proud of it. Looking back on it now, it's definitely newbie code (limited understanding of classes, so many global variables!) The appearance also looks dated, simplegui is no longer developed, it's in Python 2, and the instructions have disappeared.

Several times over the last decade, as I've improved as a developer (primarily in R), I've thought about reworking the game as a way to learn new technologies. In particular, I considered Python 3, R Shiny or Observable JS, but it was never a priority.

This year (2024), I worked through weeks 1-5 of <a href="https://cs50.harvard.edu/x/2024/" target="_blank">CS50</a>, Harvard's excellent Introduction to Computer Science course, as part of the <a href="https://contributor.r-project.org/events/c-study-group-2024/" target="_blank">C Study Group for R Contributors</a>. I enjoyed it so much that I decided to complete the course, so I needed a <a href="https://cs50.harvard.edu/x/2024/[roject]" target="_blank">final project</a>. I finally had a good reason to return to Interference.

After much deliberation, I opted to use the <a href="https://api.arcade.academy/en/latest/" target="_blank">Python Arcade</a> library as the games engine. Their <a href="https://api.arcade.academy/en/latest/tutorials/card_game/index.html" target="_blank">Solitaire tutorial</a> was a great place to start. I rewrote Interference from scratch, though obviously v1 was a useful reference. 

The Python Arcade <a href="https://github.com/ellakaye/interference-arcade" target="_blank">implementation</a> would have been v2, and I got almost all the way there with it.
The game is playable (though missing the logic that indicates when it is over), and there are no instructions either for the rules, or how to start a new round or game. 
Although pretty much done, I wasn't enamoured with the library. 
I found drag and drop to be buggy, so implemented it just with clicks, but even that froze sometimes. I didn't love how it looked, nor that you couldn't resize the window, and that it was only playable on a computer. 

Then I saw a post on Mastodon abut the <a href="https://posit.co/blog/announcing-the-2024-shiny-contest/" target="_blank">Shiny Contest</a>, 
with a submission deadline about three weeks away,
and decided to abandon work on v2 and start work on v3, using <a href="https://shiny.posit.co/py/" target="_blank">Shiny for Python</a>. Although games aren't Shiny's raison d'être, I'd seen this <a href="https://github.com/dreamRs/memory-hex" target="_blank">hex sticker memory game</a> a few years ago, so figured it should be possible.
Another motivation for the shift was that I know I'll be writing Shiny app in the future,
whereas I'm unlikely to write another Arcade game. 
I wanted to catch up on the latest Shiny innovations.

With the help of <a href="https://gallery.shinyapps.io/assistant/" target="_blank">Shiny Assistant</a> (more on my use of LLMs in the section below), 
I had translated the Arcade implementation into Shiny app in surprisingly little time,
and was very pleased I'd made the shift, because the latter looks, feels and works so much better.

From there, I've spent a couple of weeks making improvements. 
The more I've learnt about what Shiny for Python is capable of,
especially in combination with CSS and JavaScript, the more I've wanted to do!
Thankfully, the documentation is very good.
In particular, I'm pleased with the use of modals for round over and game over messages,
how the app is now styled, and the implemation of drag and drop, 
which was a substantial refactoring of the click-based approach.

There are still elements of the UI and the underlying code that I'm conscious could be improved.
In particular, the whole card grid is rendered on every drag event, and every card swap.
In retrospect, it would have been better to go with a design that laid out each card individually, 
and only re-rendered the one or two cards that moved in each go.
I did attempt a refactor along these lines, using a module for the cards, 
but haven't yet been able to get it to work.


## About the use of LLMs

Since I'm submitting this as my final project for CS50, 
I've used LLMs in accordance with their policy:

> For your final project (and your final project only!) it is reasonable to use AI-based software other than CS50’s own (e.g., ChatGPT, GitHub Copilot, Bing Chat, et al.), but the essence of the work must still be your own. You’ve learned enough to use such tools as helpers. Treat such tools as amplifying, not supplanting, your productivity. But you still must cite any use of such tools in the comments of your code.

When working on v2 (Python Arcade), my main focus was on bringing the Python code I'd written 13 years earlier for v1 up-to-date. I didn't want an LLM to write any of the game code for me.
They were invaluable in other ways though. I used ChatGPT to ask about the most Pythonic way of achieving particular goals (providing it with the minimum context/example to get a useful response), and in doing so developed a much greater understanding of Python features like list comprehension and effective use of classes. I also used ChatGPT to help debug error messages, and for questions about the Arcade library. 

The day after deciding to switch the implementation to Shiny for Python, 
I watched Winston Chang's posit::conf(2024) talk: "An assistant to learn Shiny and build Shiny apps":

> In the last few months, the best LLMs have taken a big step forward in their ability to help write code. We’ve been building a tool that uses an LLM to help you learn Shiny and build Shiny applications much faster than ever before.
>    
> If you feel like you don’t have the time to invest into learning Shiny, this might change your mind. You’ll get up and running with Shiny in no time, and you’ll be able to learn from the AI as you go. If you already know Shiny, you’ll be able to dramatically accelerate your development process, and you’ll find yourself trying out new things that wouldn’t have been worth the effort before.

<a href="https://gallery.shinyapps.io/assistant/" target="_blank">Shiny Assistant</a> combines the LLM power of <a href="https://claude.ai/" target="_blank">Claude 3.5 Sonnet</a> with <a href="https://shinylive.io/" target="_blank">ShinyLive</a> (in which you can write and run Shiny apps in a browser - no server required).

Having already done a lot of work towards v2, at this point, and with this tool, 
I was happy to let Shiny Assistant guide me through the process of converting the Arcade version to Shiny.
Using all my game logic, over a long guided conversation, Shiny Assistant produced the code for both the app's UI, 
and the server function, working out what needed to be reactive and how to keep track of game state.
I wouldn't go as far as to say it took *no time*, but it did dramatically increase the development process.
Being new to Shiny for Python, I did indeed use it as a learning tool, asking it to explain everything I didn't understand.
As I started to add features to the Shiny app that weren't present in the Arcade version, 
I was able to take what I'd learnt from Shiny Assistant, alongside the Shiny for Python docs, 
to write code myself that enhances the experience of playing the game. 
As for trying out new things that wouldn't have been worth the effort before, 
Shiny Assistant also wrote the JavaScript (a language of which I have only rudimentary knowledge and experience) 
to enable drag-and-drop, and to enable switching between tabs when clicking a link. 
It's unlikely that I would have learnt how to do that in the time available without that tool.

Shiny Assistant is still in closed beta (but actively accepting new applicants). 
It definitely has an in-development feel! It also doesn't have the answers to everything. 
We went round in circles a few times on modules, likely because modules are quite new in Shiny for Python,
so the underlying LLM doesn't know enough about them to make working suggestions.
Still, I'm sure Shiny Assistant will contine to develop as a valuable tool for Shiny newbies and seasoned developers alike.

## About me

I'm <a href="https://ellakaye.co.uk" target="_blank">Ella Kaye</a>. Professionally, I'm a Research Software Engineer at the University of Warwick, UK, 
working to foster a larger and more diverse community of contributors to base R. 
I also run <a href="https://rainbowr.org" target="_blank">rainbowR</a>, a community for LGBTQ+ folks who code in R.
For fun, I do things like this.

## Credits and code

Developed by: [Ella Kaye](https://ellakaye.co.uk)

GitHub: [EllaKaye/interference](https://github.com/EllaKaye/interference)

Version: 3.0.0 (September 2024)

License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en)

Card images from <a href="https://github.com/crobertsbmw/deckofcards" target="_blank">deckofcards</a>.