export function ProcessDefinitionField(name) {
  return {
    name,
    required: false,
    choices: [],
    help: null,
    type: 'textarea',
    display_name: 'Comment',
  };
}

export function Preset(name, processDefinitionId, variables) {
  return {
    name,
    variables,
    processDefinitionId,
  };
}

export function ProcessDefinition(id) {
  return {
    id: 'ProcessDefinition' + id,
    fields: [ProcessDefinitionField(1), ProcessDefinitionField(2)],
    presets: [
      Preset('preset1', 'ProcessDefinition' + id, {a: '1', b: '2'}),
      Preset('preset2', 'ProcessDefinition' + id, {a: '3', b: '4'}),
    ],
  };
}
