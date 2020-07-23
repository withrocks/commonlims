import merge from 'lodash/merge';

// Holds state of byIds and visibleIds. Provides methods when these two
// are updated simultaneously
export class ExpandedState {
  constructor(byIds, visibleIds) {
    this.byIds = byIds;
    this.visibleIds = visibleIds;
  }

  expandEntry(parentId, expandedByIds) {
    const ind = this.visibleIds.findIndex((e) => e == parentId);
    const expandedIds = Object.keys(expandedByIds);
    this.visibleIds.splice(ind + 1, 0, ...expandedIds);
    this.byIds = merge({}, this.byIds, expandedByIds);
    this.byIds[parentId] = this.cacheChildren(this.byIds[parentId], expandedIds);
  }

  collapseEntry(parentId) {
    if (!this.byIds[parentId].children.isFetched) {
      throw Error(
        'The parent to be collapsed are supposed to have fetched its children!'
      );
    }
    const ind = this.visibleIds.findIndex((e) => e == parentId);
    const numberChildren = this.byIds[parentId].children.cachedIds.length;
    this.visibleIds.splice(ind + 1, numberChildren);
    this.setToCollapsed(parentId);
  }
  cacheChildren(parentEntry, cachedIds) {
    return {
      ...parentEntry,
      children: {
        ...parentEntry.children,
        isFetched: true,
        isExpanded: true,
        cachedIds,
      },
    };
  }

  expandCached(parentId, expandedIds) {
    const ind = this.visibleIds.findIndex((e) => e == parentId);
    this.visibleIds.splice(ind + 1, 0, ...expandedIds);
    this.setToExpanded(parentId);
  }

  setToExpanded(entryId) {
    this.setExpandedState(entryId, true);
  }

  setToCollapsed(entryId) {
    this.setExpandedState(entryId, false);
  }

  setExpandedState(entryId, expandedState) {
    const parentEntry = this.byIds[entryId];
    this.byIds[entryId] = {
      ...parentEntry,
      children: {
        ...parentEntry.children,
        isExpanded: expandedState,
      },
    };
  }
}
