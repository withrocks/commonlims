import {Redirect, Route, IndexRoute, IndexRedirect} from 'react-router';
import React from 'react';

import App from 'app/views/app';
import HookStore from 'app/stores/hookStore';
import LazyLoad from 'app/components/lazyLoad';
import MyIssuesAssignedToMe from 'app/views/myIssues/assignedToMe';
import MyIssuesBookmarked from 'app/views/myIssues/bookmarked';
import MyIssuesViewed from 'app/views/myIssues/viewed';
import OrganizationActivity from 'app/views/organizationActivity';
import OrganizationContext from 'app/views/organizationContext';
import OrganizationCreate from 'app/views/organizationCreate';
import OrganizationDetails from 'app/views/organizationDetails';
import OrganizationHomeContainer from 'app/components/organizations/homeContainer';
import OrganizationMembers from 'app/views/settings/organizationMembers';
import OrganizationRoot from 'app/views/organizationRoot';
import OrganizationStats from 'app/views/organizationStats';
import RouteNotFound from 'app/views/routeNotFound';
import SettingsWrapper from 'app/views/settings/components/settingsWrapper';
import errorHandler from 'app/utils/errorHandler';

// CLIMS
import SubstancesContainer from 'app/views/substances/index';
import ProjectsContainer from 'app/views/projects/index';
import WorkBatchListContainer from 'app/views/workBatchList/index';
import TaskDefinitionsContainer from 'app/views/taskDefinitions/index';
import TasksContainer from 'app/views/tasks/index';
import WorkBatchDetailsContainer from 'app/views/workBatchDetails/organization/index';

function appendTrailingSlash(nextState, replace) {
  const lastChar = nextState.location.pathname.slice(-1);
  if (lastChar !== '/') {
    replace(nextState.location.pathname + '/');
  }
}

/**
 * Use react-router to lazy load a route. Use this for codesplitting containers (e.g. SettingsLayout)
 *
 * The method for lazy loading a route leaf node is using the <LazyLoad> component + `componentPromise`.
 * The reason for this is because react-router handles the route tree better and if we use <LazyLoad> it will end
 * up having to re-render more components than necesssary.
 */
const lazyLoad = (cb) => (m) => cb(null, m.default);

function routes() {
  const hooksRoutes = [];
  HookStore.get('routes').forEach((cb) => {
    hooksRoutes.push(cb());
  });

  const hooksAdminRoutes = [];
  HookStore.get('routes:admin').forEach((cb) => {
    hooksAdminRoutes.push(cb());
  });

  const hooksOrgRoutes = [];
  HookStore.get('routes:organization').forEach((cb) => {
    hooksOrgRoutes.push(cb());
  });

  const hooksSurveyRoute = [];
  HookStore.get('routes:onboarding-survey').forEach((cb) => {
    hooksSurveyRoute.push(cb());
  });

  const accountSettingsRoutes = (
    <React.Fragment>
      <IndexRedirect to="details/" />

      <Route
        path="details/"
        name="Details"
        componentPromise={() =>
          import(
            /* webpackChunkName: "AccountDetails" */ './views/settings/account/accountDetails'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route path="notifications/" name="Notifications">
        <IndexRoute
          componentPromise={() =>
            import(
              /* webpackChunkName: "AccountNotifications" */ './views/settings/account/accountNotifications'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path=":fineTuneType/"
          name="Fine Tune Alerts"
          componentPromise={() =>
            import(
              /* webpackChunkName: "AccountNotificationsFineTuning" */ './views/settings/account/accountNotificationFineTuning'
            )
          }
          component={errorHandler(LazyLoad)}
        />
      </Route>
      <Route
        path="emails/"
        name="Emails"
        componentPromise={() =>
          import(
            /* webpackChunkName: "AccountEmails" */ './views/settings/account/accountEmails'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route
        path="authorizations/"
        componentPromise={() =>
          import(
            /* webpackChunkName: "AccountAuthorizations" */ './views/settings/account/accountAuthorizations'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route name="Security" path="security/">
        <Route
          componentPromise={() =>
            import(
              /* webpackChunkName: "AccountSecurityWrapper" */ './views/settings/account/accountSecurity/accountSecurityWrapper'
            )
          }
          component={errorHandler(LazyLoad)}
        >
          <IndexRoute
            componentPromise={() =>
              import(
                /* webpackChunkName: "AccountSecurity" */ './views/settings/account/accountSecurity/index'
              )
            }
            component={errorHandler(LazyLoad)}
          />
          <Route
            path="session-history/"
            name="Session History"
            componentPromise={() =>
              import(
                /* webpackChunkName: "AccountSecuritySessionHistory" */ './views/settings/account/accountSecurity/accountSecuritySessionHistory'
              )
            }
            component={errorHandler(LazyLoad)}
          />
          <Route
            path="mfa/:authId/"
            name="Details"
            componentPromise={() =>
              import(
                /* webpackChunkName: "AccountSecurityDetails" */ './views/settings/account/accountSecurity/accountSecurityDetails'
              )
            }
            component={errorHandler(LazyLoad)}
          />
        </Route>
        /* TODO-medium: This view is broken */
        <Route
          path="mfa/:authId/enroll/"
          name="Enroll"
          componentPromise={() =>
            import(
              /* webpackChunkName: "AccountSecurityEnroll" */ './views/settings/account/accountSecurity/accountSecurityEnroll'
            )
          }
          component={errorHandler(LazyLoad)}
        />
      </Route>

      <Route path="api/" name="API">
        <IndexRedirect to="auth-tokens/" />

        <Route path="auth-tokens/" name="Auth Tokens">
          <IndexRoute
            componentPromise={() =>
              import(
                /* webpackChunkName: "ApiTokensIndex" */ './views/settings/account/apiTokens'
              )
            }
            component={errorHandler(LazyLoad)}
          />
          <Route
            path="new-token/"
            name="Create New Token"
            componentPromise={() =>
              import(
                /* webpackChunkName: "ApiTokenCreate" */ './views/settings/account/apiNewToken'
              )
            }
            component={errorHandler(LazyLoad)}
          />
        </Route>

        <Route path="applications/" name="Applications">
          <IndexRoute
            componentPromise={() =>
              import(
                /* webpackChunkName: "ApiApplications" */ './views/settings/account/apiApplications'
              )
            }
            component={errorHandler(LazyLoad)}
          />
          <Route
            path=":appId/"
            name="Details"
            componentPromise={() =>
              import(
                /* webpackChunkName: "ApiApplicationDetails" */ './views/settings/account/apiApplicationDetails'
              )
            }
            component={errorHandler(LazyLoad)}
          />
        </Route>
      </Route>

      <Route
        path="close-account/"
        name="Close Account"
        componentPromise={() =>
          import(
            /* webpackChunkName: "AccountClose" */ './views/settings/account/accountClose'
          )
        }
        component={errorHandler(LazyLoad)}
      />
    </React.Fragment>
  );

  // This is declared in the routes() function because some routes need the
  // hook store which is not available at import time.
  const orgSettingsRoutes = (
    <React.Fragment>
      <IndexRoute
        name="General"
        componentPromise={() =>
          import(
            /* webpackChunkName: "OrganizationGeneralSettings" */ './views/settings/organizationGeneralSettings'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route path="api-keys/" name="API Key">
        <IndexRoute
          componentPromise={() =>
            import(
              /* webpackChunkName: "OrganizationApiKeys" */ './views/settings/organizationApiKeys'
            )
          }
          component={errorHandler(LazyLoad)}
        />

        <Route
          path=":apiKey/"
          name="Details"
          componentPromise={() =>
            import(
              /* webpackChunkName: "OrganizationApiKeyDetails" */ './views/settings/organizationApiKeys/organizationApiKeyDetails'
            )
          }
          component={errorHandler(LazyLoad)}
        />
      </Route>

      <Route
        path="audit-log/"
        name="Audit Log"
        componentPromise={() =>
          import(
            /* webpackChunkName: "OrganizationAuditLog" */ './views/settings/organizationAuditLog'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route
        path="auth/"
        name="Auth Providers"
        componentPromise={() =>
          import(
            /* webpackChunkName: "OrganizationAuth" */ './views/settings/organizationAuth'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route path="members/" name="Members">
        <IndexRoute
          component={
            HookStore.get('component:org-members-view').length
              ? HookStore.get('component:org-members-view')[0]()
              : OrganizationMembers
          }
        />

        <Route
          path="new/"
          name="Invite"
          componentPromise={() =>
            import(
              /* webpackChunkName: "InviteMember" */ './views/settings/organizationMembers/inviteMember'
            )
          }
          component={errorHandler(LazyLoad)}
        />

        <Route
          path=":memberId/"
          name="Details"
          componentPromise={() =>
            import(
              /* webpackChunkName: "OrganizationMemberDetail" */ './views/settings/organizationMembers/organizationMemberDetail'
            )
          }
          component={errorHandler(LazyLoad)}
        />
      </Route>

      <Route
        path="rate-limits/"
        name="Rate Limits"
        componentPromise={() =>
          import(
            /* webpackChunkName: "OrganizationRateLimits" */ './views/settings/organizationRateLimits'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route
        path="settings/"
        componentPromise={() =>
          import(
            /* webpackChunkName: "OrganizationGeneralSettings" */ './views/settings/organizationGeneralSettings'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route name="Teams" path="teams/">
        <IndexRoute
          componentPromise={() =>
            import(
              /* webpackChunkName: "OrganizationTeams" */ './views/settings/organizationTeams'
            )
          }
          component={errorHandler(LazyLoad)}
        />

        <Route
          name="Team"
          path=":teamId/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "TeamDetails" */ './views/settings/organizationTeams/teamDetails'
            )
          }
          component={errorHandler(LazyLoad)}
        >
          <IndexRedirect to="members/" />
          <Route
            path="members/"
            name="Members"
            componentPromise={() =>
              import(
                /* webpackChunkName: "TeamMembers" */ './views/settings/organizationTeams/teamMembers'
              )
            }
            component={errorHandler(LazyLoad)}
          />
          <Route
            path="settings/"
            name="settings"
            componentPromise={() =>
              import(
                /* webpackChunkName: "TeamSettings" */ './views/settings/organizationTeams/teamSettings'
              )
            }
            component={errorHandler(LazyLoad)}
          />
        </Route>
      </Route>

      <Route name="Integrations" path="integrations/">
        <IndexRoute
          componentPromise={() =>
            import(
              /* webpackChunkName: "OrganizationIntegrations" */ './views/organizationIntegrations'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          name="Configure Integration"
          path=":providerKey/:integrationId/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "ConfigureIntegration" */ './views/settings/organizationIntegrations/configureIntegration'
            )
          }
          component={errorHandler(LazyLoad)}
        />
      </Route>
      <Route name="Developer Settings" path="developer-settings/">
        <IndexRoute
          componentPromise={() =>
            import(
              /* webpackChunkName: "OrganizationDeveloperSettings" */ './views/settings/organizationDeveloperSettings'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          name="New Application"
          path="new/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "sentryApplicationDetails" */ './views/settings/organizationDeveloperSettings/sentryApplicationDetails'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          name="Edit Application"
          path=":appSlug/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "sentryApplicationDetails" */ './views/settings/organizationDeveloperSettings/sentryApplicationDetails'
            )
          }
          component={errorHandler(LazyLoad)}
        />
      </Route>
    </React.Fragment>
  );

  return (
    <Route path="/" component={errorHandler(App)}>
      <Route
        path="/accept-transfer/"
        componentPromise={() =>
          import(
            /* webpackChunkName: "AcceptProjectTransfer" */ 'app/views/acceptProjectTransfer'
          )
        }
        component={errorHandler(LazyLoad)}
      />
      <Route
        path="/extensions/external-install/:providerId/:installationId"
        componentPromise={() =>
          import(
            /* webpackChunkName: "AcceptProjectTransfer" */ 'app/views/integrationInstallation'
          )
        }
        component={errorHandler(LazyLoad)}
      />

      <Route
        path="/extensions/vsts/link/"
        getComponent={(loc, cb) =>
          import(
            /* webpackChunkName: "VSTSOrganizationLink" */ './views/vstsOrganizationLink'
          ).then(lazyLoad(cb))
        }
      />

      <Redirect from="/account/" to="/settings/account/details/" />

      <Route path="/settings/" name="Settings" component={SettingsWrapper}>
        <IndexRoute
          getComponent={(loc, cb) =>
            import(
              /* webpackChunkName: "SettingsIndex" */ './views/settings/settingsIndex'
            ).then(lazyLoad(cb))
          }
        />

        <Route
          path="account/"
          name="Account"
          getComponent={(loc, cb) =>
            import(
              /* webpackChunkName: "AccountSettingsLayout" */ './views/settings/account/accountSettingsLayout'
            ).then(lazyLoad(cb))
          }
        >
          {accountSettingsRoutes}
        </Route>

        <Route
          name="Organization"
          path=":orgId/"
          component={errorHandler(OrganizationContext)}
        >
          <Route
            getComponent={(loc, cb) =>
              import(
                /* webpackChunkName: "OrganizationSettingsLayout" */ './views/settings/organization/organizationSettingsLayout'
              ).then(lazyLoad(cb))
            }
          >
            {hooksOrgRoutes}
            {orgSettingsRoutes}
          </Route>
        </Route>
      </Route>

      <Route
        path="/manage/"
        componentPromise={() =>
          import(/* webpackChunkName: "AdminLayout" */ 'app/views/admin/adminLayout')
        }
        component={errorHandler(LazyLoad)}
      >
        <IndexRoute
          componentPromise={() =>
            import(
              /* webpackChunkName: "AdminOverview" */ 'app/views/admin/adminOverview'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="buffer/"
          componentPromise={() =>
            import(/* webpackChunkName: "AdminBuffer" */ 'app/views/admin/adminBuffer')
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="relays/"
          componentPromise={() =>
            import(/* webpackChunkName: "AdminRelays" */ 'app/views/admin/adminRelays')
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="organizations/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "AdminOrganizations" */ 'app/views/admin/adminOrganizations'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="projects/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "AdminProjects" */ 'app/views/admin/adminProjects'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="queue/"
          componentPromise={() =>
            import(/* webpackChunkName: "AdminQueue" */ 'app/views/admin/adminQueue')
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="quotas/"
          componentPromise={() =>
            import(/* webpackChunkName: "AdminQuotas" */ 'app/views/admin/adminQuotas')
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="settings/"
          componentPromise={() =>
            import(
              /* webpackChunkName: "AdminSettings" */ 'app/views/admin/adminSettings'
            )
          }
          component={errorHandler(LazyLoad)}
        />
        <Route
          path="users/"
          componentPromise={() =>
            import(/* webpackChunkName: "AdminUsers" */ 'app/views/admin/adminUsers')
          }
          component={errorHandler(LazyLoad)}
        />
        {hooksAdminRoutes}
      </Route>

      <Redirect from="/share/group/:shareId/" to="/share/issue/:shareId/" />

      <Route path="/organizations/new/" component={errorHandler(OrganizationCreate)} />

      <Route path="/:orgId/" component={errorHandler(OrganizationDetails)}>
        <Route component={errorHandler(OrganizationRoot)}>
          <IndexRoute component={errorHandler(SubstancesContainer)} />

          <Route path="tasks/" component={errorHandler(TaskDefinitionsContainer)} />
          <Route
            path="tasks/:processKey/:taskKey/"
            component={errorHandler(TasksContainer)}
          />
          <Route path="workbatches/" component={errorHandler(WorkBatchListContainer)} />
          <Route path="substances/" component={errorHandler(SubstancesContainer)} />

          <Route
            path="workbatches/:groupId/"
            component={errorHandler(WorkBatchDetailsContainer)}
            ignoreScrollBehavior
          >
            <Route
              path="activity/"
              componentPromise={() =>
                import(
                  /* webpackChunkName: "WorkBatchActivity" */ './views/workBatchDetails/shared/workBatchActivity'
                )
              }
              component={errorHandler(LazyLoad)}
            />
          </Route>

          <Route
            path="/organizations/:orgId/dashboards/"
            componentPromise={() =>
              import(
                /* webpackChunkName: "OrganizationDashboardContainer" */ './views/organizationDashboard'
              )
            }
            component={errorHandler(LazyLoad)}
          >
            <IndexRoute
              componentPromise={() =>
                import(
                  /* webpackChunkName: "OverviewDashboard" */ './views/organizationDashboard/overviewDashboard'
                )
              }
              component={errorHandler(LazyLoad)}
            />
          </Route>
          <Route
            path="/organizations/:orgId/discover/"
            componentPromise={() =>
              import(
                /* webpackChunkName: "OrganizationDiscover" */ './views/organizationDiscover/index'
              )
            }
            component={errorHandler(LazyLoad)}
          >
            <Redirect path="saved/" to="/organizations/:orgId/discover/" />
            <Route path="saved/:savedQueryId/" />
          </Route>
          <Route
            path="/organizations/:orgId/activity/"
            component={errorHandler(OrganizationActivity)}
          />
          <Route
            path="/organizations/:orgId/events/"
            componentPromise={() =>
              import(
                /* webpackChunkName: "OrganizationEventsContainer" */ './views/organizationEvents'
              )
            }
            component={errorHandler(LazyLoad)}
          >
            <IndexRoute
              componentPromise={() =>
                import(
                  /* webpackChunkName: "OrganizationEvents" */ './views/organizationEvents/events'
                )
              }
              component={errorHandler(LazyLoad)}
            />
          </Route>
          <Route
            path="/organizations/:orgId/issues/"
            componentPromise={() =>
              import(
                /* webpackChunkName: "OrganizationStreamContainer" */ './views/organizationStream/container'
              )
            }
            component={errorHandler(LazyLoad)}
          >
            <Redirect from="/organizations/:orgId/" to="/organizations/:orgId/issues/" />
            <IndexRoute
              componentPromise={() =>
                import(
                  /* webpackChunkName: "OrganizationStreamOverview" */ './views/organizationStream/overview'
                )
              }
              component={errorHandler(LazyLoad)}
            />
            <Route
              path="searches/:searchId/"
              componentPromise={() =>
                import(
                  /* webpackChunkName: "OrganizationStreamOverview" */ './views/organizationStream/overview'
                )
              }
              component={errorHandler(LazyLoad)}
            />
          </Route>
          {/* Once org issues is complete, these routes can be nested under
          /organizations/:orgId/issues */}
          <Route
            path="/organizations/:orgId/issues/assigned/"
            component={errorHandler(MyIssuesAssignedToMe)}
          />
          <Route
            path="/organizations/:orgId/issues/bookmarks/"
            component={errorHandler(MyIssuesBookmarked)}
          />
          <Route
            path="/organizations/:orgId/issues/history/"
            component={errorHandler(MyIssuesViewed)}
          />

          <Route
            path="/organizations/:orgId/teams/new/"
            componentPromise={() =>
              import(/* webpackChunkName: "TeamCreate" */ './views/teamCreate')
            }
            component={errorHandler(LazyLoad)}
          />
          <Route path="/organizations/:orgId/" component={OrganizationHomeContainer}>
            <Redirect from="projects/" to="/:orgId/" />
            {hooksOrgRoutes}
            <Redirect path="teams/" to="/settings/:orgId/teams/" />
            <Redirect path="teams/your-teams/" to="/settings/:orgId/teams/" />
            <Redirect path="teams/all-teams/" to="/settings/:orgId/teams/" />
            <Redirect path="teams/:teamId/" to="/settings/:orgId/teams/:teamId/" />
            <Redirect
              path="teams/:teamId/members/"
              to="/settings/:orgId/teams/:teamId/members/"
            />
            <Redirect
              path="teams/:teamId/projects/"
              to="/settings/:orgId/teams/:teamId/projects/"
            />
            <Redirect
              path="teams/:teamId/settings/"
              to="/settings/:orgId/teams/:teamId/settings/"
            />
            <Redirect path="settings/" to="/settings/:orgId/" />
            <Redirect path="api-keys/" to="/settings/:orgId/api-keys/" />
            <Redirect path="api-keys/:apiKey/" to="/settings/:orgId/api-keys/:apiKey/" />
            <Redirect path="members/" to="/settings/:orgId/members/" />
            <Redirect path="members/new/" to="/settings/:orgId/members/new/" />
            <Redirect
              path="members/:memberId/"
              to="/settings/:orgId/members/:memberId/"
            />
            <Redirect path="rate-limits/" to="/settings/:orgId/rate-limits/" />
            <Redirect path="repos/" to="/settings/:orgId/repos/" />
            <Route path="stats/" component={errorHandler(OrganizationStats)} />
          </Route>
        </Route>
        <Route path=":projectId/" component={errorHandler(ProjectsContainer)} />
      </Route>

      {hooksRoutes}

      <Route
        path="*"
        component={errorHandler(RouteNotFound)}
        onEnter={appendTrailingSlash}
      />
    </Route>
  );
}

export default routes;
