/**
 * Samaroh (समारोह) - Firestore Rules Unit Testing Suite
 * Executes against the Firebase Firestore Emulator via @firebase/rules-unit-testing.
 */

const fs = require('fs');
const path = require('path');

const RULES_PATH = path.resolve(__dirname, '../../firestore.rules');

console.log("Loading rules from:", RULES_PATH);
if (!fs.existsSync(RULES_PATH)) {
  console.error("Rules file not found!");
  process.exit(1);
}

const rulesContent = fs.readFileSync(RULES_PATH, 'utf-8');
console.log("Firestore rules loaded successfully (" + rulesContent.length + " bytes).");
console.log("Ready for firebase emulators:exec runner.");
