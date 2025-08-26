(async function sendHelloToAllMatches() {
  const delay = ms => new Promise(res => setTimeout(res, ms));

  async function simulateTypingAndSend(selectorTextarea, message) {
    const textarea = document.querySelector(selectorTextarea);
    if (!textarea) {
      console.error("Textarea not found");
      return false;
    }

    textarea.focus();

    // Use native setter for React compatibility
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
    nativeInputValueSetter.call(textarea, '');
    textarea.dispatchEvent(new Event('input', { bubbles: true }));

    const dispatchKeyboardEvent = (type, key) => {
      textarea.dispatchEvent(new KeyboardEvent(type, {
        key: key,
        bubbles: true,
        cancelable: true,
        composed: true
      }));
    };

    const dispatchInputEvent = (inputType = 'insertText') => {
      textarea.dispatchEvent(new InputEvent('input', {
        bubbles: true,
        cancelable: true,
        data: null,
        inputType: inputType,
        composed: true
      }));
    };

    for (const char of message) {
      dispatchKeyboardEvent('keydown', char);
      dispatchKeyboardEvent('keypress', char);

      nativeInputValueSetter.call(textarea, textarea.value + char);

      dispatchInputEvent('insertText');
      textarea.dispatchEvent(new Event('change', { bubbles: true }));

      dispatchKeyboardEvent('keyup', char);

    }

    textarea.blur();
    await delay(300);

    const sendBtn = document.querySelector('button[type="submit"]');
    if (!sendBtn) {
      console.error("Send button not found");
      return false;
    }

    // Force enable the button if disabled
    if (sendBtn.disabled) sendBtn.disabled = false;
    sendBtn.classList.remove('Cur(d)', 'Pe(n)');
    sendBtn.classList.add('Cur(p)');

    sendBtn.click();
    console.log("Message sent!");
    return true;
  }

  while (true) {
    const matches = [...document.querySelectorAll('a.matchListItem')];
    if (matches.length < 4) {
      console.log("Less than 4 matches remaining, stopping.");
      break;
    }

    const match = matches[3];
    console.log(`Opening 4th match out of ${matches.length} matches...`);
    match.click();

    await delay(2000);

    const success = await simulateTypingAndSend('textarea', 'Do you have a map? I keep getting lost in your eyes.');
    if (!success) {
      console.warn("Failed to send message on this match.");
    }

    await delay(2000);

    const matchesTabBtn = document.querySelector('button[role="tab"][aria-controls][type="button"]');
    if (matchesTabBtn) {
      matchesTabBtn.click();
    } else {
      console.warn("Matches tab button not found, stopping.");
      break;
    }

    await delay(2000);
  }

  console.log("✅ All messages sent or no more matches.");
})();
