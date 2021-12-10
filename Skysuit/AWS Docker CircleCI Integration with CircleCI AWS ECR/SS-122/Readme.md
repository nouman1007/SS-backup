# Implement a CircleCI job to create docker container in ECR

## CircleCI 

Provides enterprise-class support and services, with the flexibility of a startup. We work where you work: Linux, macOS, Android, and Windows - SaaS or behind the firewall.

![arch](D:\Skysuit\AWS Docker CircleCI Integration with CircleCI AWS ECR\SS-122\arch.png)

#### Projects

A CircleCI project shares the name of the associated code repository in your VCS (GitHub or Bitbucket). Select Add Project from the CircleCI application to enter the Projects dashboard, from where you can set up and follow the projects you have access to.

On the Projects Dashboard, you can either:

- *Set Up* any project that you are the owner of in your VCS

- *Follow* any project in your organization to gain access to its pipelines and to subscribe to [email notifications](https://circleci.com/docs/2.0/notifications/) for the project’s status.

  

  #### Configuration

  CircleCI believes in *configuration as code*. Your entire continuous integration and deployment process is orchestrated through a single file called `config.yml`. The `config.yml` file is located in a folder called `.circleci` at the root of your project. CircleCI uses the YAML syntax for config, see the [Writing YAML](https://circleci.com/docs/2.0/writing-yaml/) document for basics.

  ```
  ├── .circleci
  │   ├── config.yml
  ├── README
  └── all-other-project-files-and-folders
  ```

  `config.yml` is a powerful YAML file that defines the entire pipeline for your project. For a full overview of the various keys that are used, see the [Configuration Reference](https://circleci.com/docs/2.0/configuration-reference/) page for more information.

  Your CircleCI configuration can be adapted to fit many different needs of your project. The following terms, sorted in order of granularity and dependence, describe the components of most common CircleCI projects:

  - **[Pipeline](https://circleci.com/docs/2.0/concepts/?section=getting-started#pipelines)**: Represents the entirety of your configuration. Available in CircleCI Cloud only.
  - **[Workflows](https://circleci.com/docs/2.0/concepts/?section=getting-started#workflows)**: Responsible for orchestrating multiple *jobs*.
  - **[Jobs](https://circleci.com/docs/2.0/concepts/?section=getting-started#jobs)**: Responsible for running a series of *steps* that perform commands.
  - **[Steps](https://circleci.com/docs/2.0/concepts/?section=getting-started#steps)**: Run commands (such as installing dependencies or running tests) and shell scripts to do the work required for your project.

  #### Pipeline

  pipeline is the full set of processes you run when you trigger work on your projects. Pipelines encompass your workflows, which in turn coordinate your jobs. This is all defined in your project [configuration file](https://circleci.com/docs/2.0/concepts/?section=getting-started#configuration)

  #### Orbs

  Orbs are reusable snippets of code that help automate repeated processes, speed up project setup, and make it easy to integrate with third-party tools

  #### Jobs

  Jobs are the building blocks of your config. Jobs are collections of [steps](https://circleci.com/docs/2.0/concepts/?section=getting-started#steps), which run commands/scripts as required. Each job must declare an executor that is either `docker`, `machine`, `windows` or `macos`. `machine` includes a [default image](https://circleci.com/docs/2.0/executor-intro/#machine) if not specified, for `docker` you must [specify an image](https://circleci.com/docs/2.0/executor-intro/#docker) to use for the primary container, for `macos` you must specify an [Xcode version](https://circleci.com/docs/2.0/executor-intro/#macos), and for `windows` you must use the [Windows orb](https://circleci.com/docs/2.0/executor-intro/#windows).

  #### Executor

  Each separate job defined within config will run in a unique executor. An executor can be a docker container or a virtual machine running Linux, Windows, or MacOS. Note, macOS is not currently available on self-hosted installations of CircleCI Server.

  #### Steps

  Steps are actions that need to be taken to complete your job. Steps are usually a collection of executable commands. For example, the [`checkout`](https://circleci.com/docs/2.0/configuration-reference/#checkout) step, which is a *built-in* step available across all CircleCI projects, checks out the source code for a job over SSH. Then, the `run` step allows you to run custom commands, such as executing the command `make test` using a non-login shell by default. Commands can also be defined [outside the job declaration](https://circleci.com/docs/2.0/configuration-reference/#commands-requires-version-21), making them reusable across your config.

  #### Image

  An image is a packaged system that has instructions for creating a running container. The Primary Container is defined by the first image listed in a [`.circleci/config.yml`](https://circleci.com/docs/2.0/configuration-reference/) file. This is where commands are executed for jobs using the Docker or machine executor. The Docker executor spins up a container with a Docker image. The machine executor spins up a complete Ubuntu virtual machine image.

  #### Workflows

  Workflows define a list of jobs and their run order. It is possible to run jobs concurrently, sequentially, on a schedule, or with a manual gate using an approval job.

  #### Caches

  A cache stores a file or directory of files such as dependencies or source code in object storage. Each job may contain special steps for caching dependencies from previous jobs to speed up the build.

  #### Workspaces

  Workspaces are a workflow-aware storage mechanism. A workspace stores data unique to the job, which may be needed in downstream jobs. Each workflow has a temporary workspace associated with it. The workspace can be used to pass along unique data built during a job to other jobs in the same workflow.

  #### Artifacts

  Artifacts persist data after a workflow is completed and may be used for longer-term storage of the outputs of your build process.

  #### Summary

  After a software repository on GitHub or Bitbucket is authorized and added as a project to [circleci.com](https://circleci.com/), every code change triggers automated tests in a clean container or VM. CircleCI runs each [job](https://circleci.com/docs/2.0/glossary/#job) in a separate [container](https://circleci.com/docs/2.0/glossary/#container) or VM. That is, each time your job runs CircleCI spins up a container or VM to run the job in.

  CircleCI then sends an email notification of success or failure after the tests complete. CircleCI also includes integrated [Slack and IRC notifications](https://circleci.com/docs/2.0/notifications). Code test coverage results are available from the details page for any project for which a reporting library is added.

  CircleCI may be configured to deploy code to various environments, including AWS CodeDeploy, AWS EC2 Container Service (ECS), AWS S3, Google Kubernetes Engine (GKE), Microsoft Azure, and Heroku. Other cloud service deployments are easily scripted using SSH or by installing the API client of the service with your job configuration.

  ## Deployment

  

- Create AWS ECR repository `slackcicd`

- Create AWS IAM group `CircleCI`

- Create customer managed AWS IAM policy `AllowPushPullImages`

```json
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "ecr:GetAuthorizationToken"
         ],
         "Resource":["*"]
      },
      {
         "Effect":"Allow",
         "Action":[
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage",
            "ecr:BatchCheckLayerAvailability",
            "ecr:PutImage",
            "ecr:InitiateLayerUpload",
            "ecr:UploadLayerPart",
            "ecr:CompleteLayerUpload"
         ],
         "Resource":[
            "arn:aws:ecr:us-east-1:424432388155:repository/slackcicd"
         ]
      }
   ]
}
```

- Attach the policy `AllowPushPullImages` to a group `CircleCI`
- Create IAM user `circleci` with only programmatic access and add it to `CircleCI` group
- Download `.csv` file with credentials
- Go back to Slack Bot - `https://github.com/antonputra/slackcicd` and install the following packages

```bash
$ npm install --save-dev mocha
$ npm install mocha-junit-reporter --save-dev
```

- Create test file `test/test.js`

```javascript
var assert = require('assert');
describe('Array', function() {
  describe('#indexOf()', function() {
    it('should return -1 when the value is not present', function() {
      assert.strictEqual([1, 2, 3].indexOf(4), -1);
    });
  });
});
```

- Update test command in `package.json`

```javascript
"scripts": {
  "test": "mocha --reporter mocha-junit-reporter --reporter-options mochaFile=/tmp/test-results/results.xml"
}
```

- Run test command

```bash
$ npm test
```

- Create CircleCI config file `.circleci/config.yml`

```yaml
version: 2.1
orbs:
  # https://circleci.com/developer/orbs/orb/circleci/node
  node: circleci/node@4.1.0
jobs:
  test:
    executor:
      name: node/default
      tag: 14.15.1
    steps:
    - checkout
    - node/install-packages:
        pkg-manager: npm
    - run:
        command: npm test
        name: Run Mocha tests
    - store_artifacts:
        path: /tmp/test-results
        destination: raw-test-output
    - store_test_results:
        path: /tmp/test-results
workflows:
  node-tests:
    jobs:
    - test
```

- Commit and push code to repository
- Add `aws-ecr/build-and-push-image` job

```yaml
orbs:
  # https://circleci.com/developer/orbs/orb/circleci/aws-ecr
  aws-ecr: circleci/aws-ecr@6.15.0
  ...
workflows:
  node-tests:
    jobs:
      ...
      # Envs: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_ECR_ACCOUNT_URL
      - aws-ecr/build-and-push-image:
          repo: slackcicd
          tag: "latest,v0.1.${CIRCLE_BUILD_NUM}"
          dockerfile: build/Dockerfile.prod
          path: .
          requires:
            - test
```

- Add the following environment variables to the CircleCI project

```bash
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
AWS_ECR_ACCOUNT_URL
```

- Commit and push code to repository