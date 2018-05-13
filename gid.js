function guidRandom() {
return "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = Math.random() * 16 | 0,
    v = c == "x" ? r : (r & 3 | 8);
    console.log(c)
  return v.toString(16)

}).toUpperCase()
}
gid=guidRandom()
console.log(gid)
