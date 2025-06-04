// Show loading indicator
function showLoading() {
    document.querySelector('.loading').style.display = 'block';
    document.getElementById('svgOutput').style.display = 'none';
}

// Hide loading indicator
function hideLoading() {
    document.querySelector('.loading').style.display = 'none';
    document.getElementById('svgOutput').style.display = 'block';
    document.getElementById('downloadSvgButton').style.display = 'block';
    document.getElementById('downloadPngButton').style.display = 'block';
}

// Handle file selection
document.querySelector('input[type="file"]').onchange = function(event) {
    if (event.target.files.length > 0) {
        showLoading();
        const formData = new FormData();
        formData.append('file', event.target.files[0]);
        
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('svgOutput').src = data.svg_path + '?t=' + new Date().getTime();
                hideLoading();
                // Reset all sliders to default values
                document.getElementById('minContourLen').value = 10;
                document.getElementById('minContourLenValue').textContent = '10';
                document.getElementById('strokeWidth').value = 1.0;
                document.getElementById('strokeWidthValue').textContent = '1.0';
                document.getElementById('thresholdBlockSize').value = 11;
                document.getElementById('thresholdBlockSizeValue').textContent = '11';
                document.getElementById('thresholdC').value = 2;
                document.getElementById('thresholdCValue').textContent = '2';
                document.getElementById('strokeColor').value = '#FFFFFF';
                document.getElementById('backgroundColor').value = '#000000';
                // Clear the file input to allow re-uploading the same file
                event.target.value = '';
            } else {
                alert(data.error);
                hideLoading();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while uploading the file.');
            hideLoading();
        });
    }
};

let updateTimeout;
function updateSVG() {
    const minContourLen = document.getElementById('minContourLen').value;
    const strokeWidth = document.getElementById('strokeWidth').value;
    const thresholdBlockSize = document.getElementById('thresholdBlockSize').value;
    const thresholdC = document.getElementById('thresholdC').value;
    const strokeColor = document.getElementById('strokeColor').value;
    const backgroundColor = document.getElementById('backgroundColor').value;
    
    const formData = new FormData();
    formData.append('update', 'true');
    formData.append('minContourLen', minContourLen);
    formData.append('strokeWidth', strokeWidth);
    formData.append('thresholdBlockSize', thresholdBlockSize);
    formData.append('thresholdC', thresholdC);
    formData.append('strokeColor', strokeColor);
    formData.append('backgroundColor', backgroundColor);
    
    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('svgOutput').src = data.svg_path + '?t=' + new Date().getTime();
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating parameters.');
    });
}

// Update slider values display and trigger update with debounce
document.getElementById('minContourLen').oninput = function() {
    document.getElementById('minContourLenValue').textContent = this.value;
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateSVG, 300);
};

document.getElementById('strokeWidth').oninput = function() {
    document.getElementById('strokeWidthValue').textContent = this.value;
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateSVG, 300);
};

document.getElementById('thresholdBlockSize').oninput = function() {
    document.getElementById('thresholdBlockSizeValue').textContent = this.value;
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateSVG, 300);
};

document.getElementById('thresholdC').oninput = function() {
    document.getElementById('thresholdCValue').textContent = this.value;
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateSVG, 300);
};

// Color picker change handlers
document.getElementById('strokeColor').onchange = function() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateSVG, 300);
};

document.getElementById('backgroundColor').onchange = function() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateSVG, 300);
};

// SVG download button handler
document.getElementById('downloadSvgButton').addEventListener('click', function() {
    const svgUrl = document.getElementById('svgOutput').src;
    const link = document.createElement('a');
    link.href = svgUrl;
    link.download = 'output.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// PNG download button handler
document.getElementById('downloadPngButton').addEventListener('click', function() {
    window.location.href = '/download_png';
}); 