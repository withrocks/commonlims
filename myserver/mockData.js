const substances = [
  {
    id: 100,
    version: 1,
    name: 'demoplugin-sample-100',
    properties: {
      erudite: {id: '397', name: 'erudite', display_name: 'erudite', value: 19.0},
      moxy: {id: '398', name: 'moxy', display_name: 'moxy', value: 66.0},
      sample_type: {
        id: '399',
        name: 'sample_type',
        display_name: 'sample type',
        value: 'Hydra Claw',
      },
      cool: {id: '400', name: 'cool', display_name: 'cool', value: 17.0},
    },
    type_full_name: 'clims.services.substance.SubstanceBase',
    location: null,
  },
];

module.exports = {
  substances,
};
