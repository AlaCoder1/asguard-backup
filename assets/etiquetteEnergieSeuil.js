/*
    -----------------------------------------
    Name : visibility
    Role : Add/Remove display none to inputs based on action
    -----------------------------------------
*/
function visibility(action, inputOne, inputTwo) {
    if (action === 'remove') {
        inputOne.classList.remove('d-none');
        inputOne.labels[0].classList.remove('d-none');
        inputTwo.classList.remove('d-none');
        inputTwo.labels[0].classList.remove('d-none');
    } else {
        inputOne.classList.add('d-none');
        inputOne.labels[0].classList.add('d-none');
        inputTwo.classList.add('d-none');
        inputTwo.labels[0].classList.add('d-none');
    }
}

/*
    -----------------------------------------
    Name : etiquetteEnergieSeuil
    Role : Change Visibility of inputs based on type value
    -----------------------------------------
*/
export function etiquetteEnergieSeuil() {
    const data = document.getElementById('ethiquette-donnes');
    const seuilMinOne = document.getElementById('EtiquetteEnergie_seuilMinOne');
    const seuilMaxOne = document.getElementById('EtiquetteEnergie_seuilMaxOne');
    const seuilMinTwo = document.getElementById('EtiquetteEnergie_seuilMinTwo');
    const seuilMaxTwo = document.getElementById('EtiquetteEnergie_seuilMaxTwo');

    const selectElement = document.getElementById('EtiquetteEnergie_typeEtiquette');
    if (!data) {
        visibility('add', seuilMinOne, seuilMaxOne);
        visibility('add', seuilMinTwo, seuilMaxTwo);
    } else if (data && (data.attributes[1].nodeValue < 3)) {
        const myObj = JSON.parse(data.attributes[2].nodeValue);
        visibility('add', seuilMinTwo, seuilMaxTwo);
        seuilMinOne.value = myObj.seuilMinOne;
        seuilMaxOne.value = myObj.seuilMaxOne;
    } else {
        const myObj = JSON.parse(data.attributes[2].nodeValue);
        seuilMinOne.value = myObj.seuilMinOne;
        seuilMaxOne.value = myObj.seuilMaxOne;
        seuilMinTwo.value = myObj.seuilMinTwo;
        seuilMaxTwo.value = myObj.seuilMaxTwo;
    }

    selectElement.addEventListener('change', (event) => {
        const type = event.target.value;
        if (type < 3) {
            visibility('remove', seuilMinOne, seuilMaxOne);
            visibility('add', seuilMinTwo, seuilMaxTwo);
        } else {
            visibility('remove', seuilMinOne, seuilMaxOne);
            visibility('remove', seuilMinTwo, seuilMaxTwo);
        }
    });
}