const { Builder, By, Key, until } = require('selenium-webdriver');
const assert = require("assert");

async function runTest() {
  let driver = await new Builder().forBrowser('chrome').build();
  try {
    await driver.get('https://nycrentalhistory.rcdis.co/');
    
    let url = await driver.getCurrentUrl();
    console.log("**** current URL *****", url);
    
    // Find and interact with elements
    let element = await driver.findElement(By.id('search'));
    await element.click();
    
    // Wait for results
    // await driver.wait(until.titleContains('Expected Title'), 1000);
  } catch (e) {
    console.log(e);
  } 
  finally {
    await driver.quit();
  }
}

runTest();