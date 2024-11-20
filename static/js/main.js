var products = JSON.parse(document.getElementById("products").value);
console.log(products);

for (var i = 0; i < products.length; i++) {
  document.getElementById("select1").innerHTML += `
    <option value="${i}">${products[i].product_name}</option>
  `;
  document.getElementById("select2").innerHTML += `
    <option value="${i}">${products[i].product_name}</option>
  `;
}

function item1(a) {
  var select2 = document.getElementById("select2").value;
  if (a != select2) {
    document.getElementById("img1").src = products[a].product_image;
    document.getElementById("price1").innerHTML =  products[a].product_price;
    document.getElementById("desc1").innerHTML = products[a].product_name;
    document.getElementById("brand1").innerHTML = products[a].product_rate; 
  } else {
    document.getElementById("select1").selectedIndex = 0;
    document.getElementById("img1").src = "";
    document.getElementById("price1").innerHTML = "";
    document.getElementById("desc1").innerHTML = "";
    document.getElementById("brand1").innerHTML = "";
  }
}

function item2(a) {
  var select1 = document.getElementById("select1").value;
  if (a != select1) {
    document.getElementById("img2").src = products[a].product_image;
    document.getElementById("price2").innerHTML = products[a].product_price;
    document.getElementById("desc2").innerHTML = products[a].product_name;
    document.getElementById("brand2").innerHTML = products[a].product_rate; 
  } else {
    document.getElementById("select2").selectedIndex = 0;
    document.getElementById("img2").src = "";
    document.getElementById("price2").innerHTML = "";
    document.getElementById("desc2").innerHTML = "";
    document.getElementById("brand2").innerHTML = "";
  }
}


