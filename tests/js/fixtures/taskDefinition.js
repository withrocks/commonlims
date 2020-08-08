// Example: const workbatch = TestStubs.WorkBatch(5);
export function TaskDefinition(id) {
  return {
    id: id ? id : 1,
    name: 'Test' + (id ? id : 1),
    organization: 1,
    handler: 'somehandler2',
    created: '2019-06-12T13:07:13.490Z',
    extra_fields: '',
    num_comments: 0,
    status: 0,
  };
}
