// Create a global variable for the utterance
let utterance = new SpeechSynthesisUtterance();

const speakButton = document.getElementById('speakButton');
const resultDiv = document.getElementById('result');
const queryDiv = document.getElementById('query'); 

speakButton.addEventListener('click', function() {
    window.speechSynthesis.cancel();
    utterance.text = 'Speak now.';
    window.speechSynthesis.speak(utterance);
    const recognition = new window.webkitSpeechRecognition();
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.addEventListener('result', function(event) {
        const transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');

        if (event.results[0].isFinal) {
            // Clear previous results
            resultDiv.innerHTML = '';
            // Announce that the search results are being fetched
            utterance.text = `Searching results for ${transcript}.`;
            window.speechSynthesis.speak(utterance);
            // Display the query and make it clickable
            queryDiv.textContent = `Query: ${transcript}`;
            queryDiv.addEventListener('click', function() {
                if (window.speechSynthesis.speaking) {
                    window.speechSynthesis.cancel();
                } else {
                    utterance.text = `Your query is ${transcript}`;
                    window.speechSynthesis.speak(utterance);
                }
            });
            
            fetch('http://localhost:8000/rerank/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: transcript, count: 5 })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // Announce that the search results are ready
                utterance.text = `Search results for ${transcript} are here.`;
                window.speechSynthesis.speak(utterance);
                data.forEach((item, index) => {
                    // Create a new div element for each item
                    const itemDiv = document.createElement('div');
                    // Show all the details in the tab with clear separation
                    itemDiv.innerHTML = `<strong>Title:</strong> ${item.title}<br>
                                         <strong>Description:</strong> ${item.description.split(' ').slice(0, 20).join(' ')}...<br>
                                         <strong>Published at:</strong> ${item.publishedAt.split('T')[0]}<br>
                                         <strong>Length:</strong> ${item.length}<br>
                                         <strong>View count:</strong> ${item.viewCount}`;
                  
                    // Add a click event listener to speak the item details
                    itemDiv.addEventListener('click', function() {
                        // If speaking, stop
                        if (window.speechSynthesis.speaking) {
                            window.speechSynthesis.cancel();
                        } else {
                            utterance.text = itemDiv.textContent;
                            window.speechSynthesis.speak(utterance);
                        }
                    });

                    // Add a double click event listener to navigate to the item URL
                    itemDiv.addEventListener('dblclick', function() {
                        window.speechSynthesis.cancel();
                        setTimeout(function() {
                            window.location.href = item.url;
                        }, 1000); // Delay of 200 milliseconds
                    });

                    // Append the item div to the result div
                    resultDiv.appendChild(itemDiv);
                });
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error.message);
            });
        }
    });

    // Start the speech recognition
    setTimeout(() => recognition.start(), 1000);
});
