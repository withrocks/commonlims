// Example: const workBatch = TestStubs.TaskDefinition(5);
export function WorkBatch(id) {
  return {
    id: id,
    name: 'WorkBatch' + id,
    handler: '',
    created_at: '2020-03-18T21:55:21.255768Z',
    updated_at: '2020-03-18T21:55:21.255788Z',
    extra_fields: '',
    num_comments: 0,
    status: 0,
    organization: 1,
  };
}
