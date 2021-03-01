document.addEventListener('DOMContentLoaded', function () {
    const api_key = "9f310a96277549df8442fd2103b75ebc";
    var m = new Date();
    var dateString = m.getUTCFullYear() + "-" + ("0" + (m.getUTCMonth()+1)).slice(-2) + "-" + ("0" + m.getUTCDate()).slice(-2);
    
    getNews(dateString, api_key);
})


function getNews(date, API_KEY) {

    var mainContainer = document.querySelector('.true-body');

    fetch(`https://newsapi.org/v2/everything?q=tech&from=${date}&sortBy=popularity&apiKey=${API_KEY}`)
    .then((response) => {
        return response.json();
    })
    
    .then((data) => {
        data.articles.forEach((element) => {
            console.log(element.title);
            var div1 = document.createElement("div");
            div1.className = "row";

            var div2 = document.createElement("div");
            div2.className = "col s12 m7";

            var div3 = document.createElement("div");
            div3.className = "card";

            var div41 = document.createElement("div");
            div41.className = "card-image";

            var img = document.createElement("img");
            img.src = element.urlToImage;

            var span = document.createElement("span");
            span.className = "card-title";
            span.innerHTML = element.title;

            var div42 = document.createElement("div");
            div42.className = "card-content";

            var p = document.createElement("p");
            p.innerHTML = element.description;

            var div43 = document.createElement("div");
            div43.className = "card-action";

            var a = document.createElement("a");
            a.href = element.url;
            a.innerHTML = "View full article";

            div1.appendChild(div2);
            div2.appendChild(div3);
            div3.appendChild(div41);
            div41.appendChild(img);
            div41.appendChild(span);
            div3.appendChild(div42);
            div42.appendChild(p);
            div3.appendChild(div43);
            div43.appendChild(a);
            mainContainer.appendChild(div1);
        })
    })
}
