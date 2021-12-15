from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from python_stuff import grid_translator


opt = Options()
opt.add_experimental_option("debuggerAddress", "localhost:8989")
driver_path = r"C:\proj\venv_qa\Lib\site-packages\tir-2.0-py3.7.egg\tir\technologies\core\drivers\chromedriver.exe"
driver = webdriver.Chrome(executable_path=driver_path, chrome_options=opt)

execute_js_code = driver.execute_script("""
    /* enable XPATH */
    function getElementByXpath(path) {
        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    }

    /* find anchor for pin */
    var mainWindow = getElementByXpath('//div[contains(@class, "tpanel twidget dict-tpanel")]/div[contains(@class, "tpanel twidget dict-tpanel align-center")]');
    var div5 = document.createElement("button");
    mainWindow.append(div5);

    /* styles for first type of anchor - panel ma3 */
    var style_button = document.createElement('style');
    style_button.type = 'text/css';
    style_button.innerHTML = '.cssClass { border: 2px solid; font-size: 12px; border-radius: 4px; padding: 10px; background-color: #75cdff; }';
    mainWindow.append(style_button);

    div5.classList.add('cssClass');
    var arr_fields = document.querySelectorAll('div[name*="M->"]');


    function projectBoxMouseOver() {
        div5.textContent = "";
        div5.textContent = this.attributes.name.textContent;
    }


    function projectBoxMouseOut() {
        div5.textContent = "Aim at the field!";
        
    }


    for (let i = 0; i < arr_fields.length; i++) {
        arr_fields[i].addEventListener('mouseover', projectBoxMouseOver);
        arr_fields[i].addEventListener('mouseout', projectBoxMouseOut);
    }

""")

data_dict = driver.execute_script("""
function get_all_grids() {
    let all_tables = document.getElementsByTagName("table")
    let results = []

    all_tables.forEach(function(entry) {
    if (entry.rows.length === 2) {
        results.push(entry)}
    });
    return results;
}
const grids = get_all_grids()

function grids_dict(grids) {
    let grid_dict = {}
    grids.forEach(function (entry, i){
        let help_list = []
        let children = entry.tHead.rows[0].children;
        children.forEach(function(entry) {
            help_list.push(entry.innerText)
        });
        grid_dict[i] = help_list
        });
    return grid_dict
}

const grid_dict1 = grids_dict(grids)
return grid_dict1
""")
new_data_dict = grid_translator(data_dict)
driver.execute_script("""
function get_all_grids() {
    let all_tables = document.getElementsByTagName("table")
    let results = []

    all_tables.forEach(function(entry) {
    if (entry.rows.length === 2) {
        results.push(entry)}
    });
    return results;
}
const grids = get_all_grids()
function grid_filler(grids, grid_dict) {
    grids.forEach(function (grid, grid_num){
        let children = grid.tHead.rows[0].children;
        let head = grid.tHead
        let new_head = head.clone()
        let columns = grid.getElementsByTagName('colgroup')[0].children
        grid.insertAdjacentElement('afterbegin', new_head)
        children.forEach(function(child, child_num) {
            if (typeof grid_dict[grid_num] === 'object'){
                let name_len = grid_dict[grid_num][child_num].length
                child.innerHTML = grid_dict[grid_num][child_num]
                columns[child_num].style.width = `${name_len*10}px`
            }
            else {
                child.innerHTML = 'ХХХ'
            }
        })
    })
}
grid_filler(grids, """+str(new_data_dict)+""")
""")
