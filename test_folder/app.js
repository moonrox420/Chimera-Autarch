// Sample JavaScript file for testing
var name = "test";
function processData(data) {
    console.log("Processing data:", data);
    return data.map(function(item) {
        return item * 2;
    });
}

const config = {
    apiUrl: "http://localhost:8080",
    debug: true
};

module.exports = processData;
