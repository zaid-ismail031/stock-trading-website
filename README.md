# STOCK TRADING WEBSITE

This website allows users to demo-trade with 9 real-life stocks i.e. Apple Inc, Electronic Arts Inc, Alphabet Inc Class A, Activision Blizzard, Inc. and so on. 

The live price of a single share is pulled from the IEX Cloud API whenever the "/stocks" page is refreshed. 

Users can view detailed histories of each stock, over several different time ranges (1 month, 3 months, 1 year and so on). These histories are also pulled from IEX Cloud (Note: 
the stock history data is fake and is purely for demonstration purposes, as it is using IEX Cloud's developer API). These histories are visually represented using a line graph 
generated using the chart.js library. 

Each user is given $10000 of funds to demo-trade with. They can choose to purchase as many shares of each stock as they want (as long as they have the funds for it). When shares are 
purchased, the user's open position can viewed on the "/open" (Open Positions) page. This page shows the position they entered the market at, and the current value of that position. 
Clicking the close button will sell all the shares the user "owns" of that particular stock. Note that the user's funds is updated dynamically on the top right of the navbar, whenever
a position is closed successfully.

When a position is closed, it is added to the "/close" (Closed Positions) page. This page shows the net profits a user has made from each stock that that they have traded.

The "/news" (News) page shows tech related news to aid users in their trading strategies (as all the stocks on this website are tech related). Headlines, pictures and short descriptions
are shown. Clicking on "View Full Article" will take users to the full article. The news information from the newsapi.org API.

