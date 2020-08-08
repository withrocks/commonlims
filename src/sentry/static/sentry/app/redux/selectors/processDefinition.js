import {createSelector} from 'reselect';
// import {Map} from 'immutable';

const getProcessDefinitions = (state) => state.processDefinition.byIds;

// function processAndVariablesToMapKey(process, variables) {
//   console.log("CREATING KEY WITH", process, variables);
//   return Map({...variables, __process: process});
// }

// Fetches all available presets from all available processDefinitions
export const getPresetsById = createSelector(
  [getProcessDefinitions],
  (processDefinitions) => {
    // Returns all presets basd on all processDefinitions we've got. The presets are sorted by ID.
    const allPresets = [];

    for (const procDef of Object.values(processDefinitions)) {
      allPresets.push(...procDef.presets);
    }
    const presetsById = {};
    //let mapProcessAndVarsToPreset = Map();

    for (const entry of allPresets) {
      // We add a new key for the preset that's not available in the backend:
      entry.id = entry.processDefinitionId + '/' + entry.name;
      presetsById[entry.id] = entry;

      // const key = processAndVariablesToMapKey(entry.processDefinitionId, entry.variables);
      // console.log("PRESET", key);
      // mapProcessAndVarsToPreset = mapProcessAndVarsToPreset.set(key, entry.id);
      // console.log("PRESET", mapProcessAndVarsToPreset);
      // console.log("PRESET OK", mapProcessAndVarsToPreset[key]);
    }
    return presetsById;
  }
);

// export const getPresetBySelection =
// TODO: Find the correct PRESET based on the selection of the current variables
//
