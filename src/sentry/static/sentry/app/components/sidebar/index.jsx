import $ from 'jquery';
import {ThemeProvider} from 'emotion-theming';
import {isEqual} from 'lodash';
import {withRouter, browserHistory} from 'react-router';
import PropTypes from 'prop-types';
import React from 'react';
import Reflux from 'reflux';
import createReactClass from 'create-react-class';
import styled, {css} from 'react-emotion';
import queryString from 'query-string';
import * as icons from 'app/components/icons';

import {extractSelectionParameters} from 'app/components/organizations/globalSelectionHeader/utils';
import {hideSidebar, showSidebar} from 'app/actionCreators/preferences';
import {load as loadIncidents} from 'app/actionCreators/incidents';
import {t} from 'app/locale';
import ConfigStore from 'app/stores/configStore';
import PreferencesStore from 'app/stores/preferencesStore';
import SentryTypes from 'app/sentryTypes';
import space from 'app/styles/space';
import theme from 'app/utils/theme';
import withLatestContext from 'app/utils/withLatestContext';

import Incidents from './incidents';
import OnboardingStatus from './onboardingStatus';
import SidebarDropdown from './sidebarDropdown';
import SidebarHelp from './help';
import SidebarItem from './sidebarItem';

class Sidebar extends React.Component {
  static propTypes = {
    router: PropTypes.object,
    organization: SentryTypes.Organization,
    collapsed: PropTypes.bool,
    location: PropTypes.object,
  };

  constructor(props) {
    super(props);
    this.state = {
      horizontal: false,
      currentPanel: '',
      showPanel: false,
    };

    if (!window.matchMedia) {
      return;
    }
    // TODO(billy): We should consider moving this into a component
    this.mq = window.matchMedia(`(max-width: ${theme.breakpoints[0]})`);
    this.mq.addListener(this.handleMediaQueryChange);
    this.state.horizontal = this.mq.matches;
  }

  componentDidMount() {
    const {router} = this.props;
    document.body.classList.add('body-sidebar');
    document.addEventListener('click', this.documentClickHandler);

    loadIncidents();

    // router can potentially not exist in server side (django) views
    // Otherwise when we change routes using collapsed sidebar, the tooltips will remain after
    // route changes.
    this.routerListener =
      router &&
      router.listen(() => {
        $('.tooltip').tooltip('hide');
      });

    this.doCollapse(this.props.collapsed);
  }

  componentWillReceiveProps(nextProps) {
    const {collapsed, location} = this.props;
    const nextLocation = nextProps.location;

    // Close active panel if we navigated anywhere
    if (nextLocation && location && location.pathname !== nextLocation.pathname) {
      this.hidePanel();
    }

    if (collapsed === nextProps.collapsed) {
      return;
    }

    this.doCollapse(nextProps.collapsed);
  }

  // Sidebar doesn't use children, so don't use it to compare
  // Also ignore location, will re-render when routes change (instead of query params)
  shouldComponentUpdate({children, location, ...nextPropsToCompare}, nextState) {
    const {
      children: _children, // eslint-disable-line no-unused-vars
      location: _location, // eslint-disable-line no-unused-vars
      ...currentPropsToCompare
    } = this.props;

    return (
      !isEqual(currentPropsToCompare, nextPropsToCompare) ||
      !isEqual(this.state, nextState)
    );
  }

  componentWillUnmount() {
    document.removeEventListener('click', this.documentClickHandler);
    document.body.classList.remove('body-sidebar');

    if (this.mq) {
      this.mq.removeListener(this.handleMediaQueryChange);
      this.mq = null;
    }

    // Unlisten to router changes
    if (this.routerListener) {
      this.routerListener();
    }
  }

  doCollapse(collapsed) {
    if (collapsed) {
      document.body.classList.add('collapsed');
    } else {
      document.body.classList.remove('collapsed');
    }
  }

  toggleSidebar = () => {
    const {collapsed} = this.props;

    if (!collapsed) {
      hideSidebar();
    } else {
      showSidebar();
    }
  };

  hashChangeHandler = () => {
    if (window.location.hash == '#welcome') {
      this.setState({showTodos: true});
    }
  };

  handleMediaQueryChange = (changed) => {
    this.setState({
      horizontal: changed.matches,
    });
  };

  // Hide slideout panel
  hidePanel = () => {
    if (!this.state.sidePanel && this.state.currentPanel === '') {
      return;
    }

    this.setState({
      showPanel: false,
      currentPanel: '',
    });
  };

  // Keep the global selection querystring values in the path
  navigateWithGlobalSelection = (pathname, evt) => {
    const globalSelectionRoutes = [
      'dashboards',
      'issues',
      'events',
      'releases',
      'user-feedback',
    ].map((route) => `/organizations/${this.props.params.orgId}/${route}/`);

    // Only keep the querystring if the current route matches one of the above
    if (globalSelectionRoutes.includes(this.props.location.pathname)) {
      const query = extractSelectionParameters(this.props.location.query);

      // Handle cmd-click (mac) and meta-click (linux)
      if (evt.metaKey) {
        const q = queryString.stringify(query);
        evt.currentTarget.href = `${evt.currentTarget.href}?${q}`;
        return;
      }

      evt.preventDefault();
      browserHistory.push({pathname, query});
    }

    this.hidePanel();
  };

  // Show slideout panel
  showPanel = (panel) => {
    this.setState({
      showPanel: true,
      currentPanel: panel,
    });
  };

  togglePanel = (panel, e) => {
    if (this.state.currentPanel === panel) {
      this.hidePanel();
    } else {
      this.showPanel(panel);
    }
  };

  documentClickHandler = (evt) => {
    // If click occurs outside of sidebar, close any active panel
    if (this.sidebar && !this.sidebar.contains(evt.target)) {
      this.hidePanel();
    }
  };

  render() {
    const {organization, collapsed} = this.props;
    const {currentPanel, showPanel, horizontal} = this.state;
    const config = ConfigStore.getConfig();
    const user = ConfigStore.get('user');
    const hasPanel = !!currentPanel;
    const orientation = horizontal ? 'top' : 'left';
    const sidebarItemProps = {
      orientation,
      collapsed,
      hasPanel,
    };
    const hasOrganization = !!organization;

    const hasSentry10 = hasOrganization && new Set(organization.features).has('sentry10');

    return (
      <StyledSidebar innerRef={(ref) => (this.sidebar = ref)} collapsed={collapsed}>
        <SidebarSectionGroup>
          <SidebarSection>
            <SidebarDropdown
              onClick={this.hidePanel}
              orientation={orientation}
              collapsed={collapsed}
              org={organization}
              user={user}
              config={config}
            />
          </SidebarSection>
          {hasOrganization && (
            <React.Fragment>
              <SidebarSection>
                <SidebarItem
                  {...sidebarItemProps}
                  index
                  onClick={this.hidePanel}
                  icon={<icons.AvailableWork />}
                  label={t('Available Work')}
                  to={`/${organization.slug}/tasks/`}
                />
                <SidebarItem
                  {...sidebarItemProps}
                  index
                  onClick={this.hidePanel}
                  icon={<icons.WorkInProgress />}
                  label={t('Work in Progress')}
                  to={`/${organization.slug}/work-batches/`}
                />
                <SidebarItem
                  {...sidebarItemProps}
                  index
                  onClick={this.hidePanel}
                  icon={<icons.Substance />}
                  label={t('Samples')}
                  to={`/${organization.slug}/substances/`}
                />
                <SidebarItem
                  {...sidebarItemProps}
                  index
                  onClick={this.hidePanel}
                  icon={<icons.Projects />}
                  label={t('Projects')}
                  to={`/${organization.slug}/projects/`}
                />
              </SidebarSection>
            </React.Fragment>
          )}

          {hasOrganization && (
            <React.Fragment>
              {!hasSentry10 && (
                <React.Fragment>
                  <SidebarSection>
                    <SidebarItem
                      {...sidebarItemProps}
                      onClick={this.hidePanel}
                      icon={<icons.AssignedToMe />}
                      label={t('Assigned to me')}
                      to={`/organizations/${organization.slug}/issues/assigned/`}
                    />
                    <SidebarItem
                      {...sidebarItemProps}
                      onClick={this.hidePanel}
                      icon={<icons.Bookmarks />}
                      label={t('Bookmarks')}
                      to={`/organizations/${organization.slug}/issues/bookmarks/`}
                    />
                    <SidebarItem
                      {...sidebarItemProps}
                      onClick={this.hidePanel}
                      icon={<icons.RecentlyViewed />}
                      label={t('Recently viewed')}
                      to={`/organizations/${organization.slug}/issues/history/`}
                    />
                  </SidebarSection>

                  <SidebarSection>
                    <SidebarItem
                      {...sidebarItemProps}
                      onClick={this.hidePanel}
                      icon={<icons.Activity />}
                      label={t('Activity')}
                      to={`/organizations/${organization.slug}/activity/`}
                    />
                    <SidebarItem
                      {...sidebarItemProps}
                      onClick={this.hidePanel}
                      icon={<icons.Stats />}
                      label={t('Stats')}
                      to={`/organizations/${organization.slug}/stats/`}
                    />
                  </SidebarSection>
                </React.Fragment>
              )}

              <SidebarSection>
                <SidebarItem
                  {...sidebarItemProps}
                  onClick={this.hidePanel}
                  icon={<icons.Settings />}
                  label={t('Settings')}
                  to={`/settings/${organization.slug}/`}
                />
              </SidebarSection>
            </React.Fragment>
          )}
        </SidebarSectionGroup>

        {hasOrganization && (
          <SidebarSectionGroup>
            <SidebarSection>
              <SidebarHelp
                orientation={orientation}
                collapsed={collapsed}
                hidePanel={this.hidePanel}
                organization={organization}
              />
              <Incidents
                orientation={orientation}
                collapsed={collapsed}
                showPanel={showPanel}
                currentPanel={currentPanel}
                onShowPanel={() => this.togglePanel('statusupdate')}
                hidePanel={this.hidePanel}
              />
            </SidebarSection>

            {!horizontal && (
              <SidebarSection noMargin>
                <OnboardingStatus
                  org={organization}
                  currentPanel={currentPanel}
                  onShowPanel={() => this.togglePanel('todos')}
                  showPanel={showPanel}
                  hidePanel={this.hidePanel}
                  collapsed={collapsed}
                />
              </SidebarSection>
            )}

            {!horizontal && (
              <SidebarSection>
                <SidebarCollapseItem
                  data-test-id="sidebar-collapse"
                  {...sidebarItemProps}
                  icon={
                    collapsed ? (
                      <icons.ExpandLeftSidebar />
                    ) : (
                      <icons.CollapseLeftSidebar />
                    )
                  }
                  label={collapsed ? t('Expand') : t('Collapse')}
                  onClick={this.toggleSidebar}
                />
              </SidebarSection>
            )}
          </SidebarSectionGroup>
        )}
      </StyledSidebar>
    );
  }
}

const SidebarContainer = withRouter(
  createReactClass({
    displayName: 'SidebarContainer',
    mixins: [Reflux.listenTo(PreferencesStore, 'onPreferenceChange')],
    getInitialState() {
      return {
        collapsed: PreferencesStore.getInitialState().collapsed,
      };
    },

    onPreferenceChange(store) {
      if (store.collapsed === this.state.collapsed) {
        return;
      }

      this.setState({
        collapsed: store.collapsed,
      });
    },

    render() {
      return (
        <ThemeProvider theme={theme}>
          <Sidebar {...this.props} collapsed={this.state.collapsed} />
        </ThemeProvider>
      );
    },
  })
);

export {Sidebar};
export default withLatestContext(SidebarContainer);

const responsiveFlex = css`
  display: flex;
  flex-direction: column;

  @media (max-width: ${theme.breakpoints[0]}) {
    flex-direction: row;
  }
`;

const StyledSidebar = styled('div')`
  background: ${(p) => p.theme.sidebar.background};
  background: linear-gradient(${(p) => p.theme.gray4}, ${(p) => p.theme.gray5});
  color: ${(p) => p.theme.sidebar.color};
  line-height: 1;
  padding: 12px 19px 2px; /* Allows for 32px avatars  */
  width: ${(p) => p.theme.sidebar.expandedWidth};
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  justify-content: space-between;
  z-index: ${(p) => p.theme.zIndex.sidebar};
  ${responsiveFlex};
  ${(p) => p.collapsed && `width: ${p.theme.sidebar.collapsedWidth};`};

  @media (max-width: ${(p) => p.theme.breakpoints[0]}) {
    top: 0;
    left: 0;
    right: 0;
    height: ${(p) => p.theme.sidebar.mobileHeight};
    bottom: auto;
    width: auto;
    padding: 0;
    align-items: center;
  }
`;

const SidebarSectionGroup = styled('div')`
  ${responsiveFlex};
  flex-shrink: 0;
`;

const SidebarSection = styled(SidebarSectionGroup)`
  ${(p) => !p.noMargin && `margin: ${space(1)} 0`};
  @media (max-width: ${(p) => p.theme.breakpoints[0]}) {
    margin: 0 ${space(1)};
  }
`;

const SidebarCollapseItem = styled(SidebarItem)`
  @media (max-width: ${(p) => p.theme.breakpoints[0]}) {
    display: none;
  }
`;
