let currentFilename = null;
let metadata = null;
let compareFilename = null;
let compareMetadata = null;
let comparingSlices = false;

// DOM elements
const fileInput = document.getElementById('fileInput');
const fileInputB = document.getElementById('fileInputB');
const uploadBtn = document.getElementById('uploadBtn');
const uploadBtnB = document.getElementById('uploadBtnB');
const fileInfo = document.getElementById('fileInfo');
const fileInfoB = document.getElementById('fileInfoB');
const controls = document.getElementById('controls');
const vizMode = document.getElementById('vizMode');
const sliceControls = document.getElementById('sliceControls');
const volumeControls = document.getElementById('volumeControls');
const renderBtn = document.getElementById('renderBtn');
const compareBtn = document.getElementById('compareBtn');
const compare3DBtn = document.getElementById('compare3DBtn');
const sliceSlider = document.getElementById('sliceSlider');
const sliceIndex = document.getElementById('sliceIndex');
const axisSelect = document.getElementById('axisSelect');
const loading = document.getElementById('loading');
const output = document.getElementById('output');
const cmapSelect = document.getElementById('cmapSelect');

// Slice + compare views
const singleSliceView = document.getElementById('singleSliceView');
const singleSliceImage = document.getElementById('singleSliceImage');
const compareSliceView = document.getElementById('compareSliceView');
const sliceSliderA = document.getElementById('sliceSliderA');
const sliceIndexA = document.getElementById('sliceIndexA');
const sliceSliderB = document.getElementById('sliceSliderB');
const sliceIndexB = document.getElementById('sliceIndexB');
const compareImageA = document.getElementById('compareImageA');
const compareImageB = document.getElementById('compareImageB');

// 3-plane views
const threePlaneView = document.getElementById('threePlaneView');
const sliderX = document.getElementById('sliderX');
const sliderY = document.getElementById('sliderY');
const sliderZ = document.getElementById('sliderZ');
const sliceXInput = document.getElementById('sliceX');
const sliceYInput = document.getElementById('sliceY');
const sliceZInput = document.getElementById('sliceZ');
const planeImageX = document.getElementById('planeImageX');
const planeImageY = document.getElementById('planeImageY');
const planeImageZ = document.getElementById('planeImageZ');

// 3D
const threeDView = document.getElementById('threeDView');
const threeDContainer = document.getElementById('threeDContainer');

const axisMap = { x: 0, y: 1, z: 2 };

// Event listeners
uploadBtn.addEventListener('click', uploadFile);
uploadBtnB.addEventListener('click', uploadFileB);
vizMode.addEventListener('change', handleModeChange);
renderBtn.addEventListener('click', generateVisualization);
compareBtn.addEventListener('click', handleCompareClick);
compare3DBtn.addEventListener('click', generateCompare3D);

axisSelect.addEventListener('change', handleAxisChange);
cmapSelect.addEventListener('change', handlePaletteChange);

sliceSlider.addEventListener('input', () => {
    sliceIndex.value = sliceSlider.value;
    if (!comparingSlices) {
        debouncedRenderSingle();
    }
});

sliceIndex.addEventListener('input', () => {
    clampToBounds(sliceIndex, sliceSlider);
    if (!comparingSlices) {
        debouncedRenderSingle();
    }
});

[ [sliceSliderA, sliceIndexA, 'A'], [sliceSliderB, sliceIndexB, 'B'] ].forEach(
    ([slider, number, key]) => {
        slider.addEventListener('input', () => {
            number.value = slider.value;
            if (comparingSlices) {
                renderComparePanel(key);
            }
        });
        number.addEventListener('input', () => {
            clampToBounds(number, slider);
            if (comparingSlices) {
                renderComparePanel(key);
            }
        });
    }
);

[
    [sliderX, sliceXInput, 'x'],
    [sliderY, sliceYInput, 'y'],
    [sliderZ, sliceZInput, 'z']
].forEach(([slider, number, axisKey]) => {
    slider.addEventListener('input', () => {
        number.value = slider.value;
        if (vizMode.value === '3plane') {
            debouncedRenderPlane(axisKey);
        }
    });
    number.addEventListener('input', () => {
        clampToBounds(number, slider);
        if (vizMode.value === '3plane') {
            debouncedRenderPlane(axisKey);
        }
    });
});

function debounce(fn, delay = 150) {
    let timer = null;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

const debouncedRenderSingle = debounce(() => renderSingleSlice(true), 120);
const debouncedRenderPlane = debounce((axisKey) => renderPlane(axisKey, true), 120);

function handleModeChange() {
    comparingSlices = false;
    toggleControls();
    if (!currentFilename) return;

    if (vizMode.value === 'slice') {
        renderSingleSlice(true);
    } else if (vizMode.value === '3plane') {
        renderAllPlanes(true);
    } else if (vizMode.value === '3d') {
        render3D();
    }
}

async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) {
        showMessage('Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';

        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.success) {
            currentFilename = data.filename;
            metadata = data.metadata;
            showMetadata(data.metadata);
            controls.style.display = 'block';

            updateSliceBounds();
            setSliceDefaults();
            updateCompareBounds();
            setThreePlaneDefaults();
            toggleControls();
            renderSingleSlice(true);
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showMessage(`Upload failed: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload File';
    }
}

async function uploadFileB() {
    const file = fileInputB.files[0];
    if (!file) {
        showMessageB('Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        uploadBtnB.disabled = true;
        uploadBtnB.textContent = 'Uploading...';

        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.success) {
            compareFilename = data.filename;
            compareMetadata = data.metadata;
            showMetadataB(data.metadata);
            updateCompareBounds();
            updateCompareButtons();
        } else {
            showMessageB(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showMessageB(`Upload failed: ${error.message}`, 'error');
    } finally {
        uploadBtnB.disabled = false;
        uploadBtnB.textContent = 'Upload Second File';
    }
}

function handleAxisChange() {
    updateSliceBounds();
    setSliceDefaults();
    updateCompareBounds();

    if (!currentFilename) return;
    if (vizMode.value === 'slice') {
        if (comparingSlices) {
            renderCompareSlices();
        } else {
            renderSingleSlice(true);
        }
    }
}

function handlePaletteChange() {
    if (!currentFilename) return;
    const mode = vizMode.value;
    if (mode === 'slice' && !comparingSlices) {
        renderSingleSlice(true);
    } else if (mode === 'slice' && comparingSlices) {
        renderCompareSlices();
    } else if (mode === '3plane') {
        renderAllPlanes(true);
    } else if (mode === '3d') {
        render3D();
    }
}

function clampToBounds(numberInput, slider) {
    const max = parseInt(slider.max || '0', 10);
    const val = Math.max(0, Math.min(parseInt(numberInput.value || 0, 10), max));
    numberInput.value = val;
    slider.value = val;
}

function updateSliceBounds() {
    if (!metadata) return;
    const axis = parseInt(axisSelect.value, 10);
    const maxVal = metadata.shape[axis] - 1;
    sliceIndex.max = maxVal;
    sliceSlider.max = maxVal;
}

function setSliceDefaults() {
    if (!metadata) return;
    const axis = parseInt(axisSelect.value, 10);
    const mid = Math.floor(metadata.shape[axis] / 2);
    sliceIndex.value = mid;
    sliceSlider.value = mid;
}

function updateCompareBounds() {
    if (metadata) {
        const axis = parseInt(axisSelect.value, 10);
        const maxA = metadata.shape[axis] - 1;
        sliceSliderA.max = maxA;
        sliceIndexA.max = maxA;
        const valA = sliceSliderA.value ? Math.min(parseInt(sliceSliderA.value, 10), maxA) : Math.floor(maxA / 2);
        sliceSliderA.value = valA;
        sliceIndexA.value = valA;
    }
    if (compareMetadata) {
        const axis = parseInt(axisSelect.value, 10);
        const maxB = compareMetadata.shape[axis] - 1;
        sliceSliderB.max = maxB;
        sliceIndexB.max = maxB;
        const valB = sliceSliderB.value ? Math.min(parseInt(sliceSliderB.value, 10), maxB) : Math.floor(maxB / 2);
        sliceSliderB.value = valB;
        sliceIndexB.value = valB;
    }
}

function setThreePlaneDefaults() {
    if (!metadata) return;
    const [sxMax, syMax, szMax] = metadata.shape.map((dim) => dim - 1);
    sliderX.max = sxMax;
    sliderY.max = syMax;
    sliderZ.max = szMax;
    sliceXInput.max = sxMax;
    sliceYInput.max = syMax;
    sliceZInput.max = szMax;

    sliderX.value = sliceXInput.value = Math.floor(sxMax / 2);
    sliderY.value = sliceYInput.value = Math.floor(syMax / 2);
    sliderZ.value = sliceZInput.value = Math.floor(szMax / 2);
}

function toggleControls() {
    const mode = vizMode.value;

    sliceControls.style.display = mode === 'slice' ? 'block' : 'none';
    volumeControls.style.display = mode === '3d' ? 'block' : 'none';

    const showSlice = mode === 'slice' && currentFilename && !comparingSlices;
    const showCompare = mode === 'slice' && currentFilename && compareFilename && comparingSlices;
    const show3Plane = mode === '3plane' && currentFilename;
    const show3D = mode === '3d' && currentFilename;

    singleSliceView.style.display = showSlice ? 'block' : 'none';
    compareSliceView.style.display = showCompare ? 'block' : 'none';
    threePlaneView.style.display = show3Plane ? 'block' : 'none';
    threeDView.style.display = show3D ? 'block' : 'none';

    updateCompareButtons();
}

function updateCompareButtons() {
    const mode = vizMode.value;
    compareBtn.style.display = mode === 'slice' ? 'inline-block' : 'none';
    compare3DBtn.style.display = mode === '3d' ? 'inline-block' : 'none';

    compareBtn.disabled = !(currentFilename && compareFilename) || mode !== 'slice';
    compare3DBtn.disabled = !(currentFilename && compareFilename) || mode !== '3d';
}

function setLoading(isLoading) {
    loading.style.display = isLoading ? 'block' : 'none';
    renderBtn.disabled = isLoading;
}

async function generateVisualization() {
    if (!currentFilename) {
        showMessage('Please upload a file first', 'error');
        return;
    }

    comparingSlices = false;
    toggleControls();
    setLoading(true);

    try {
        const mode = vizMode.value;
        if (mode === 'slice') {
            await renderSingleSlice(false);
        } else if (mode === '3plane') {
            await renderAllPlanes(false);
        } else if (mode === '3d') {
            await render3D();
        }
    } catch (error) {
        output.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        setLoading(false);
    }
}

async function renderSingleSlice(isAuto = true) {
    if (!currentFilename) return;
    const axis = parseInt(axisSelect.value, 10);
    const sliceIdx = parseInt(sliceSlider.value || 0, 10);

    try {
        if (!isAuto) setLoading(true);
        const imageUrl = await fetchSliceImage(currentFilename, axis, sliceIdx, cmapSelect.value);
        singleSliceImage.src = imageUrl;
        singleSliceView.style.display = 'block';
        output.innerHTML = '';
    } catch (error) {
        output.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        if (!isAuto) setLoading(false);
    }
}

async function handleCompareClick(event) {
    event.preventDefault();
    if (!currentFilename || !compareFilename) {
        showMessage('Upload both files before comparing', 'error');
        return;
    }
    comparingSlices = true;
    toggleControls();
    await renderCompareSlices();
}

async function renderCompareSlices() {
    if (!currentFilename || !compareFilename) return;
    try {
        setLoading(true);
        await Promise.all([renderComparePanel('A'), renderComparePanel('B')]);
        compareSliceView.style.display = 'block';
        singleSliceView.style.display = 'none';
        output.innerHTML = '';
    } catch (error) {
        output.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        setLoading(false);
        updateCompareButtons();
    }
}

async function renderComparePanel(which) {
    const axis = parseInt(axisSelect.value, 10);
    const cmap = cmapSelect.value;

    const isA = which === 'A';
    const filename = isA ? currentFilename : compareFilename;
    const slider = isA ? sliceSliderA : sliceSliderB;
    const imgEl = isA ? compareImageA : compareImageB;

    const sliceIdx = parseInt(slider.value || 0, 10);
    const imageUrl = await fetchSliceImage(filename, axis, sliceIdx, cmap);
    imgEl.src = imageUrl;
}

async function renderAllPlanes(isAuto = true) {
    await Promise.all([
        renderPlane('x', isAuto),
        renderPlane('y', isAuto),
        renderPlane('z', isAuto)
    ]);
}

async function renderPlane(axisKey, isAuto = true) {
    if (!metadata || !currentFilename) return;
    const slider = axisKey === 'x' ? sliderX : axisKey === 'y' ? sliderY : sliderZ;
    const imgEl = axisKey === 'x' ? planeImageX : axisKey === 'y' ? planeImageY : planeImageZ;
    const sliceIdx = parseInt(slider.value || 0, 10);
    const axis = axisMap[axisKey];

    try {
        if (!isAuto) setLoading(true);
        const imageUrl = await fetchSliceImage(currentFilename, axis, sliceIdx, cmapSelect.value);
        imgEl.src = imageUrl;
    } catch (error) {
        output.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        if (!isAuto) setLoading(false);
    }
}

async function fetchSliceImage(filename, axis, sliceIdx, cmap) {
    const response = await fetch('/visualize/slice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename, axis, slice_idx: sliceIdx, cmap })
    });

    if (!response.ok) {
        throw new Error('Slice rendering failed');
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
}

async function render3D() {
    if (!currentFilename) return;
    const opacity = document.getElementById('opacitySelect').value;
    const cmap = cmapSelect.value;
    const renderMode = document.getElementById('renderModeSelect').value;

    try {
        setLoading(true);
        threeDContainer.innerHTML = '';
        threeDView.style.display = 'block';

        // Fetch interactive 3D HTML from Plotly endpoint
        const response = await fetch('/visualize/3d', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                filename: currentFilename, 
                opacity: opacity, 
                cmap: cmap,
                render_mode: renderMode  // 'slices', 'isosurface', or 'volume'
            })
        });

        if (!response.ok) {
            throw new Error('3D rendering failed');
        }

        const htmlContent = await response.text();
        
        // Create iframe with the HTML content
        const iframe = document.createElement('iframe');
        iframe.className = 'three-d-frame';
        iframe.style.width = '100%';
        iframe.style.height = '800px';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '8px';
        
        threeDContainer.appendChild(iframe);
        
        // Write content to iframe
        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(htmlContent);
        iframe.contentWindow.document.close();
        
        output.innerHTML = '';
    } catch (error) {
        output.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        setLoading(false);
    }
}

async function generateCompare3D(event) {
    if (event) event.preventDefault();
    if (!currentFilename || !compareFilename) {
        showMessage('Upload both files before comparing', 'error');
        return;
    }

    setLoading(true);
    threeDView.style.display = 'block';
    singleSliceView.style.display = 'none';
    compareSliceView.style.display = 'none';

    const opacity = document.getElementById('opacitySelect').value;
    const cmap = cmapSelect.value;

    try {
        threeDContainer.innerHTML = '';
        
        // Fetch interactive 3D comparison HTML from Plotly endpoint
        const response = await fetch('/visualize/compare3d', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename_a: currentFilename,
                filename_b: compareFilename,
                opacity: opacity,
                cmap: cmap
            })
        });

        if (!response.ok) {
            throw new Error('3D comparison rendering failed');
        }

        const htmlContent = await response.text();
        
        // Create iframe with the HTML content
        const iframe = document.createElement('iframe');
        iframe.className = 'three-d-frame';
        iframe.style.width = '100%';
        iframe.style.height = '800px';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '8px';
        
        threeDContainer.appendChild(iframe);
        
        // Write content to iframe
        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(htmlContent);
        iframe.contentWindow.document.close();
        
        output.innerHTML = '';
    } catch (error) {
        output.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    } finally {
        setLoading(false);
        updateCompareButtons();
    }
}

function showMetadata(meta) {
    fileInfo.className = 'info-box show success';
    fileInfo.innerHTML = `
        <strong>✓ File loaded successfully!</strong><br>
        <strong>Format:</strong> ${meta.format}<br>
        <strong>Shape:</strong> ${meta.shape.join(' × ')}<br>
        <strong>Data Type:</strong> ${meta.dtype}<br>
        <strong>Value Range:</strong> [${meta.value_range[0].toFixed(2)}, ${meta.value_range[1].toFixed(2)}]<br>
        <strong>Mean:</strong> ${meta.mean.toFixed(2)} | <strong>Std:</strong> ${meta.std.toFixed(2)}
    `;
}

function showMetadataB(meta) {
    fileInfoB.className = 'info-box show success';
    fileInfoB.innerHTML = `
        <strong>✓ Second file loaded!</strong><br>
        <strong>Format:</strong> ${meta.format}<br>
        <strong>Shape:</strong> ${meta.shape.join(' × ')}<br>
        <strong>Data Type:</strong> ${meta.dtype}
    `;
}

function showMessage(message, type = 'info') {
    fileInfo.className = `info-box show ${type}`;
    fileInfo.innerHTML = message;
}

function showMessageB(message, type = 'info') {
    fileInfoB.className = `info-box show ${type}`;
    fileInfoB.innerHTML = message;
}

toggleControls();

