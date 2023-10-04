const buttons = document.querySelectorAll('.download-button');
const saveButton = document.querySelectorAll('.save-button');
const generateButton = document.querySelector('.gen-btn')
const searchSpinner = document.querySelector('.searching')
const downloadSpinner = document.querySelectorAll('.downloading')
const boxes = document.querySelectorAll('.box')



function startAnimation(index) {
    downloadSpinner[index].style.display = "block";
    buttons[index].innerHTML = "Cancel"
};


function endAnimation(index) {
    downloadSpinner[index].style.display = "none";
    buttons[index].style.display = "none";
    saveButton[index].style.display = "block";
};


function cancelDownload() {
//  cancel download
    console.log("cancel button pressed")
}


async function downloadSong(index) {
    startAnimation(index)   // start animation near the button that was clicked

    // get the button that was clicked using index and get its attributes
    const clickedButton = buttons[index];
    const songInfo = clickedButton.getAttribute('song-info');

    const response = await fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ songInfo: songInfo })
    });

    const data = await response.json();
    if (data.value === true) {
        // Do something when the value is true
        endAnimation(index) // stop the animation if value is true
        console.log('Received true from Python! Performing an action.');
    } else {
        console.log('Received false from Python.');
    }
};


function checkClickedButton(index) {
    const buttonValue = buttons[index].innerHTML;
    if (buttonValue === 'Download' || buttonValue === 'Download All') {
        downloadSong(index); // send the index number of the clicked button
    }
    else if (buttonValue === 'Cancel') {
        console.log("cancel button clicked")
    }
    else {
        console.log("none")
    }
}


buttons.forEach((button, index) => {
    button.addEventListener('click', ()=> {
        checkClickedButton(index);
    });
});


// hide the search list while searching
generateButton.addEventListener('click',()=> {
    searchSpinner.style.display = "block";
    for (let box of boxes) {
        box.style.display = "none";
    }
})
