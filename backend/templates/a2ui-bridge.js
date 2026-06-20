const A2UI = {
  /**
   * Trigger a target action or event hook in the Gemini Enterprise Agent.
   * @param {string} actionName Name of the action.
   * @param {object} payload Context details to pass to the event hook.
   */
  triggerAction: function(actionName, payload = {}) {
    if (window.parent) {
      window.parent.postMessage({
        type: 'a2ui_action',
        action: actionName,
        data: payload
      }, '*');
    } else {
      console.warn("A2UI Event Bridge: No parent window detected to postMessage to.");
    }
  },

  /**
   * Save the current widget selections or UI state to prevent rehydration loss.
   * @param {string} widgetName Unique identifier of the widget block.
   * @param {object} context State key-values to serialize.
   */
  saveWidgetSelection: function(widgetName, context = {}) {
    this.triggerAction('save_widget_selection', {
      tf_name_state: widgetName,
      ...context
    });
  },

  /**
   * Listen for incoming state updates sent from the parent frame.
   * @param {function} callback Receives the updated state dictionary.
   */
  onStateUpdate: function(callback) {
    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'state_update') {
        callback(event.data.state);
      }
    });
  }
};
