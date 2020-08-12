/*
 * Copyright 2020 Univention GmbH
 *
 * https://www.univention.de/
 *
 * All rights reserved.
 *
 * The source code of this program is made available
 * under the terms of the GNU Affero General Public License version 3
 * (GNU AGPL V3) as published by the Free Software Foundation.
 *
 * Binary versions of this program provided by Univention to you as
 * well as other copyrighted, protected or trademarked materials like
 * Logos, graphics, fonts, specific documentations and configurations,
 * cryptographic keys etc. are subject to a license agreement between
 * you and Univention and not subject to the GNU AGPL V3.
 *
 * In the case you use this program under the terms of the GNU AGPL V3,
 * the program is provided in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public
 * License with the Debian GNU/Linux or Univention distribution in file
 * /usr/share/common-licenses/AGPL-3; if not, see
 * <https://www.gnu.org/licenses/>.
 */
/*global define*/

/**
 * @module portal/Portal
 */
define([
	"dojo/_base/declare",
	"dojo/_base/lang",
	"dojo/_base/array",
	"dojo/dom-class",
	"dojo/dom-construct",
	"dojo/on",
	"dojo/on/debounce",
	"dojo/query",
	"dojo/topic",
	"dojo/io-query",
	"dojo/regexp",
	"dijit/_WidgetBase",
	"dijit/_TemplatedMixin",
	"dijit/_WidgetsInTemplateMixin",
	"dijit/form/Button", // TODO put in umc/widgets
	"dijit/form/ToggleButton", // TODO put in umc/widgets
	"dijit/a11yclick",
	"umc/widgets/TextBox",
	"umc/menu/Menu",
	"umc/menu",
	"umc/tools",
	"umc/i18n/tools",
	"put-selector/put",
	"./links",
	"./_PortalIframeTabsContainer",
	"./_PortalIframesContainer",
	"./NotificationsButton",
	"./portalContent",
	"login",
	"umc/i18n!portal"
], function(
	declare, lang, array, domClass, domConstruct, on, onDebounce, query, topic, ioQuery, regexp, _WidgetBase, _TemplatedMixin,
	_WidgetsInTemplateMixin, Button, ToggleButton, a11yclick, TextBox, Menu, menu, tools, i18nTools, put, portalLinks,
	_PortalIframeTabsContainer, _PortalIframesContainer, NotificationsButton, portalContent, login, _
) {
	var locale = i18nTools.defaultLang().replace(/-/, '_');

	var PortalSearchBox = declare("PortalSearchBox", [TextBox], {
		intermediateChanges: true,

		constructor: function() {
			this._baseClass = 'portalSearchBox';
			this.baseClass += ' ' + this._baseClass;
		}
	});

	var PortalMobileIframeTabsButton = declare("PortalMobileIframeTabsButton", [ToggleButton], {
		buildRendering: function() {
			this.inherited(arguments);
			this.counter = put(this.domNode, 'div.portal__mobileIframeTabsButton__counter');
		},

		count: '',
		_setCountAttr: function(count) {
			this.counter.innerHTML = count ? count : '';
		}
	});

	return declare("Portal", [_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {
		templateString: `
			<div class="portal">
				<div class="portal__header">
					<div
						class="portal__header__left"
						tabindex="0"
						data-dojo-attach-point="headerLeftNode"
					>
						<img
							class="dijitDisplayNone"
							alt="Portal logo"
							data-dojo-attach-point="portalLogoNode"
						>
						<h2
							data-dojo-attach-point="portalTitleNode"
						></h2>
					</div>
					<div
						class="portal__iframeTabs"
						data-dojo-type="portal/_PortalIframeTabsContainer"
						data-dojo-attach-point="iframeTabs"
					></div>
					<div class="portal__header__stretch"></div>
					<div
						class="portal__header__right"
						data-dojo-attach-point="headerRightNode"
					>
						<button
							class="portal__mobileIframeTabsButton ucsIconButton"
							data-dojo-type="PortalMobileIframeTabsButton"
							data-dojo-attach-point="mobileIframeTabsButton"
							data-dojo-props="
								iconClass: 'iconTabs',
								showLabel: false
							"
						><div>foo</div></button>
						<button
							class="ucsIconButton"
							data-dojo-type="dijit/form/ToggleButton"
							data-dojo-attach-point="toggleSearchButton"
							data-dojo-props="
								iconClass: 'iconSearch',
								showLabel: false
							"
						></button>
						<button
							data-dojo-type="NotificationsButton"
							data-dojo-attach-point="notificationsButton"
						></button>
						<button
							class="ucsIconButton"
							data-dojo-type="dijit/form/ToggleButton"
							data-dojo-attach-point="toggleMenuButton"
							data-dojo-props="
								iconClass: 'iconMenu',
								showLabel: false
							"
						></button>
					</div>
				</div>
				<div class="portal__background"></div>
				<div
					class="portal__categories"
					data-dojo-attach-point="categoriesNode"
				></div>
				<div
					class="portal__folder dijitDisplayNone"
					data-dojo-attach-point="foldersNode"
				></div>
				<div
					class="portal__iframes dijitDisplayNone"
					data-dojo-type="portal/_PortalIframesContainer"
					data-dojo-attach-point="iframesContainer"
				></div>
				<div
					class="portal__loginIframeWrapper dijitDisplayNone"
					data-dojo-attach-point="loginIframeWrapper"
				></div>
				<div
					class="portal__mobileIframeTabs overlaybg dijitDisplayNone"
					data-dojo-type="portal/_PortalIframeTabsContainer"
					data-dojo-attach-point="mobileIframeTabs"
				></div>
				<div
					data-dojo-type="umc/menu/Menu"
					data-dojo-props="
						showLoginHeader: true,
						loginCallbacks: this.loginCallbacks
					"
				></div>
				<div
					class="appDescription dijitDisplayNone"
					data-dojo-attach-point="hoveredAppDescriptionNode"
				></div>
				<div
					class="portal__search"
					data-dojo-attach-point="portalSearchBoxWrapperNode"
				>
					<div
						data-dojo-type="PortalSearchBox"
						data-dojo-attach-point="portalSearchBox"
					></div>
				</div>
			</div>
		`,

		portalLogo: null,
		_setPortalLogoAttr: function(src) {
			tools.toggleVisibility(this.portalLogoNode, !!src);
			if (src) {
				var src = lang.replace('{0}?{1}', [src, Date.now()])
				this.portalLogoNode.src = src;
			}
			this._set('portalLogo', src);
		},

		portalTitle: '',
		_setPortalTitleAttr: function(title) {
			this.portalTitleNode.innerHTML = title;
			document.title = title;
			this._set('portalTitle', title);
		},

		hoveredApp: null,
		// TODO own widget
		_setHoveredAppAttr: function(entry) {
			this.hoveredAppDescriptionNode.innerHTML = '';
			if (entry) {
				var header = put(this.hoveredAppDescriptionNode, 'div.appDescription__header');
				put(header, this._renderApp(entry, true));
				put(header, 'div.appDescription__name', entry.name);
				put(this.hoveredAppDescriptionNode, 'div.appDescription__description',
						entry.description);
			}
			tools.toggleVisibility(this.hoveredAppDescriptionNode, !!entry);
			this._set('hoveredApp', entry);
		},

		menuOpen: false,
		_setMenuOpenAttr: function(open) {
			if (open) {
				this.set('searchActive', false);
				menu.open();
			} else {
				menu.close();
			}
			this._set('menuOpen', open);
		},
		_bindMenuOpenAttr: function() {
			menu.on('open', () => {
				this.toggleMenuButton.set('checked', true);
			});
			menu.on('close', () => {
				this.toggleMenuButton.set('checked', false);
			});
			this.toggleMenuButton.watch('checked', (_attrName, _oldChecked, checked) => {
				this.set('menuOpen', checked);
				// TODO _changeAttrValue?
			});
		},

		openFolder: null,
		_setOpenFolderAttr: function(folder) {
			domClass.toggle(document.body, 'scrollLess', !!folder);
			tools.toggleVisibility(this.foldersNode, !!folder);

			this.foldersNode.innerHTML = '';
			if (folder) {
				var background = put(this.foldersNode, 'div.portal__folder__overlay.overlaybg');
				on(background, 'click', evt => {
					if (evt.target === background) {
						this.set('openFolder', null);
					}
				});

				var wrapper = put(background, 'div.portal__folder__wrapper');
				var closeButton = new Button({
					showLabel: false,
					iconClass: 'iconX',
					'class': 'ucsIconButton',
					onClick: evt => {
						this.set('openFolder', null);
					}
				});
				put(wrapper, closeButton.domNode);
				var box = put(wrapper, 'div.box');
				var carrousell = put(box, 'div.carrousell');
				var slide = put(carrousell, 'div.slide')
				let counter = 0;
				let slides = 1;
				for (const entry of folder.entries) {
					const tileNode = this._renderApp(entry);
					put(slide, tileNode);
					counter++;
					if (counter === 9) {
						counter = 0;
						slides++;
						slide = put(carrousell, 'div.slide')
					}
				}

				if (slides >= 2) {
					var nav = put(box, 'div.nav');
					for (let x = 0; x < slides; x++) {
						let b = put(nav, 'div.bubble');
						if (x === 0) {
							put(b, '.bubble--active');
						}
						on(b, 'click', evt => {
							query('.bubble', nav).removeClass('bubble--active');
							put(nav.children[x], '.bubble--active');
							carrousell.style.left = ((x * 720) * -1) + 'px';
						});
					}
				}

				// TODO
				let title = 'Title';
				put(wrapper, 'h1', title);

				put(this.foldersNode, background);
			}
			this._set('openFolder', folder);
		},

		selectedIframeId: null,
		_setSelectedIframeIdAttr: function(id) {
			domClass.toggle(document.body, 'scrollLess', id);
			this.iframeTabs.set('selectedIframeId', id);
			this.iframesContainer.set('selectedIframeId', id);
			tools.toggleVisibility(this.iframesContainer, !!id);
			this._set('selectedIframeId', id);
		},

		iframes: null,
		_setIframesAttr: function(iframes) {
			this.mobileIframeTabsButton.set('count', iframes.length);
			this.iframeTabs.set('iframes', iframes);
			this.mobileIframeTabs.set('iframes', iframes);
			this.iframesContainer.set('iframes', iframes);
			if (!iframes.map(iframe => iframe.id).includes(this.selectedIframeId)) {
				this.set('selectedIframeId', null);
			}
			this._resizeIframeTabs();
			this._set('iframes', iframes);
		},

		_loginIframe: null,
		showLoginIframe: function(saml) {
			if (!this._loginIframe) {
				var target = saml ? '/univention/saml/' : '/univention/login/';
				var url = target + '?' + ioQuery.objectToQuery({
					'location': '/univention/portal/loggedin/',
					username: tools.status('username'),
					lang: i18nTools.defaultLang()
				});

				this._loginIframe = new _PortalIframe({
					iframe: {
						url: url
					}
				});

				this._loginIframe.iframeNode.addEventListener('load', () => {
					var pathname = lang.getObject('contentWindow.location.pathname', false,
							this._loginIframe.iframeNode);
					if (pathname === '/univention/portal/loggedin/') {
						login.start(null, null, true).then(() => {
							this._refresh();
						});
						tools.toggleVisibility(this.loginIframeWrapper, false);
						this._loginIframe.destroyRecursive();
					}
				});
				this.loginIframeWrapper.appendChild(this._loginIframe.domNode);
			}
			tools.toggleVisibility(this.loginIframeWrapper, true);
		},


		_reloadCss() {
			// FIXME? instead of reloading the portal.css file,
			// use styles.insertCssRule to display the style
			// changes made after the first site load

			// reload the portal.css file
			var re = /.*\/portal.css\??\d*$/;
			var links = document.getElementsByTagName('link');
			var link = array.filter(links, function(ilink) {
				return re.test(ilink.href);
			})[0];
			if (!link) {
				return;
			}
			var href = link.href;
			if (href.indexOf('?') !== -1) {
				href = href.substr(0, href.indexOf('?'));
			}
			href += lang.replace('?{0}', [Date.now()]);
			link.href = href;
		},

		_refresh: function() {
			portalContent.reload().then(() => {
				this._reloadCss();
				this.set('content', portalContent.content());
				this._addLinks();
			});
		},

		content: null,

		_filteredContent: null,
		_set_filteredContentAttr: function(_filteredContent) {
			this.categoriesNode.innerHTML = '';
			for (const category of _filteredContent) {
				const categoryNode = this._renderCategory(category);
				put(this.categoriesNode, categoryNode);
			}
			this._set('_filteredContent', _filteredContent);
		},
		_compute_filteredContent: function() {
			if (!this.searchActive || !this.searchTerm) {
				return this.content;
			} else {
				let searchTerm = regexp.escapeString(this.searchTerm);
				searchTerm = searchTerm.replace(/\\\*/g, '.*');
				searchTerm = searchTerm.replace(/ /g, '\\s+');
				const re = new RegExp(searchTerm, 'i');
				const matchesSearch = (entry, re) => re.test(entry.name) || re.test(entry.description);

				return this.content.map(category => {
					const newCat = { ...category }; // shallow copy
					newCat.entries = newCat.entries.map(entry => {
						if (entry.type === 'entry') {
							return entry;
						} else {
							const newFolder = { ...entry }; // shallow copy
							newFolder.entries = newFolder.entries.filter(entry => {
								return matchesSearch(entry, re);
							});
							return newFolder;
						}
					}).filter(entry => {
						if (entry.type === 'entry') {
							return matchesSearch(entry, re);
						} else {
							return entry.entries.length > 0;
						}
					});
					return newCat;
				}).filter(category => {
					return category.entries.length > 0;
				});
			}
		},
		_bind_filteredContentAttr: function() {
			for (const name of ['searchActive', 'content', 'searchTerm']) {
				this.watch(name, () => {
					this.set('_filteredContent', this._compute_filteredContent());
				});
			}
		},

		_renderCategory: function(category) {
			const categoryNode = put('div.portal__category');
			put(categoryNode, 'h2.portal__category__title', category.title);
			const tilesNode = put(categoryNode, 'div.portal__category__tiles');

			for (const entry of category.entries) {
				const tileNode = entry.type === 'entry'
					? this._renderApp(entry)
					: this._renderFolder(entry);
				put(tilesNode, tileNode);
			}
			return categoryNode;
		},

		_renderApp: function(entry, asThumbnail) {
			const { dn, name, href, bgc, logo, linkTarget } = entry;

			if (asThumbnail) {
				const _tileNode = `
					<div
						class="tile__box--thumbnail"
						style="background: ${bgc}"
					>
						<img 
							class="tile__logo"
							src="${logo}"
							alt="${name} logo"
						>
					</div>
				`.trim();
				const tileNode = domConstruct.toDom(_tileNode);

				return tileNode;
			} else {
				const _tileNode = `
					<a
						class="tileLink"
						href="${href}"
					>
						<div class="tile app">
							<div
								class="tile__box"
								style="background: ${bgc}"
							>
								<img 
									class="tile__logo"
									src="${logo}"
									alt="${name} logo"
								>
							</div>
							<span class="tile__name">${name}</span>
						</div>
					</a>
				`.trim();
				const tileNode = domConstruct.toDom(_tileNode);

				switch (linkTarget) {
					case 'samewindow':
						break;
					case 'newwindow':
						tileNode.target = '_blank';
						tileNode.rel = 'noopener';
						break;
					case 'embedded':
						tileNode.onclick = function(evt) {
							evt.preventDefault();
							topic.publish('/portal/iframes/open', dn, name, logo, href);
						};
						break;
				}

				on(tileNode, 'focus', evt => {
					this.set('hoveredApp', entry);
				});
				on(tileNode, 'blur', evt => {
					this.set('hoveredApp', null);
				});
				on(tileNode, 'mouseenter', evt => {
					this.set('hoveredApp', entry);
				});
				on(tileNode, 'mouseleave', evt => {
					this.set('hoveredApp', null);
				});
				return tileNode;
			}
		},

		_renderFolder: function(folder) {
			const { dn, name } = folder;

			const _folderNode = `
				<div class="tile">
					<div
						class="tile__box tile__box--folder"
					>
						<div class="tile__thumbnails"></div>
					</div>
					<span class="tile__name">${name}</span>
				</div>
			`.trim();
			const folderNode = domConstruct.toDom(_folderNode);

			const container = folderNode.querySelector('.tile__thumbnails');
			for (let x = 0; x < Math.min(folder.entries.length, 9); x++) {
				const thumbnailNode = this._renderApp(folder.entries[x], true);
				put(container, thumbnailNode);
			}

			on(folderNode, 'click', evt => {
				this.set('openFolder', folder);
			});
			return folderNode;
		},

		constructor: function() {
			this._addeduserLinkIds = [];
			this._addedmiscLinkIds = [];
			this.loginCallbacks = {
				login: () => {
					login.start(null, null, true, (saml) => {
						this.showLoginIframe(saml);
					});
				}
			};
			this.iframes = [];
			// TODO remove
			this.iframes = [
				{
					'id': 'bar',
					url: 'http://www.youtube.com/embed/0JCUH5daCCE',
					logoUrl: 'http://10.200.28.70/univention/portal/icons/entries/umc-domain.svg',
					title: 'bar'
				}, 
				{
					'id': 'baz',
					url: 'http://www.youtube.com/embed/dNBLq6aLpCA',
					logoUrl: 'http://10.200.28.70/univention/portal/icons/entries/umc-domain.svg',
					title: 'baz'
				}
			];
			this.portalLogo = portalContent.logo();
			this.portalTitle = portalContent.title();
			this.content = portalContent.content();
		},

		searchTerm: '',
		_setSearchTermAttr: function(searchTerm) {
			this.portalSearchBox.set('value', searchTerm);
			this._set('searchTerm', searchTerm);
		},
		_bindSearchTermAttr: function() {
			console.log('bind searchTerm called');
			on(this.portalSearchBox, 'change', searchTerm => {
				if (searchTerm !== this.searchTerm) {
					this._changeAttrValue('searchTerm', searchTerm);
				}
			});
		},

		showMobileIframeTabs: false,
		_setShowMobileIframeTabsAttr: function(showTabs) {
			domClass.toggle(document.body, 'scrollLess', showTabs);
			tools.toggleVisibility(this.mobileIframeTabs, showTabs);

			this.mobileIframeTabsButton.set('checked', showTabs);
			domClass.toggle(this.mobileIframeTabs, 'portal__mobileIframeTabs--open', showTabs);
			this._set('showMobileIframeTabs', showTabs);
		},
		_bindShowMobileIframeTabsAttr: function() {
			this.mobileIframeTabsButton.watch('checked', (_attrName, _oldChecked, checked) => {
				this.set('showMobileIframeTabs', checked);
				// TODO _changeAttrValue
			});
			// TODO should this be closeable in a different way too
		},

		searchActive: false,
		_setSearchActiveAttr: function(searchActive) {
			if (searchActive) {
				this.set('showMobileIframeTabs', false);
				this.set('menuOpen', false);

				this.set('selectedIframeId', null);
			}

			this.toggleSearchButton.set('checked', searchActive);
			domClass.toggle(this.portalSearchBoxWrapperNode, 'portal__search--open', searchActive);
			this.portalSearchBox.set('disabled', !searchActive);
			if (searchActive) {
				this.portalSearchBox.focus();
			}
			this._set('searchActive', searchActive);
		},
		_bindSearchActiveAttr: function() {
			this.toggleSearchButton.watch('checked', (_attrName, _oldChecked, checked) => {
				this.set('searchActive', checked);
				// TODO _changeAttrValue?
			});
			on(this.portalSearchBox, 'keyup', evt => {
				if (evt.key === "Escape") {
					this.set('searchActive', false);
				}
			});
		},

		mobileTabsView: false,
		_setMobileTabsViewAttr: function(isTrue) {
			tools.toggleVisibility(this.iframeTabs, !isTrue);
			tools.toggleVisibility(this.mobileIframeTabsButton, isTrue);
			this._set('mobileTabsView', isTrue);
		},


		postCreate: function() {
			this.inherited(arguments);

			// iframes, selectedIframeId
			on(this.headerLeftNode, a11yclick, () => {
				this.set('selectedIframeId', null);
			});
			topic.subscribe('/portal/iframes/open', (id, title, logoUrl, url) => {
				this.set('iframes', [
					...this.iframes,
					{
						id,
						title,
						logoUrl,
						url
					}
				]);
				this.set('selectedIframeId', id);
			});
			topic.subscribe('/portal/iframes/close', id => {
				this.set('iframes', this.iframes.filter(iframe => iframe.id !== id));
			});
			topic.subscribe('/portal/iframes/select', id => {
				this.set('showMobileIframeTabs', false);
				this.set('selectedIframeId', id);
			});
			// iframes, selectedIframeId end


			on(window, onDebounce('resize', 200), () => {
				this.resize();
			});

			this._addLinks();
		},

		_addeduserLinkIds: null,
		_addedmiscLinkIds: null,
		_addLinks: function() {
			const linkCats = portalContent.links();

			for (const cat in linkCats) {
				const links = linkCats[cat];
				const basePrio = cat === 'user' ? 150 : -150;
				const addedIds = this[`_added${cat}LinkIds`];
				if (links.length && !addedIds.length) {
					menu.addSeparator({
						priority: basePrio
					});
				}

				for (const link of links) {
					if (!addedIds.includes(link.dn)) {
						addedIds.push(link.dn);
						var linkPrio = basePrio;
						if (link.priority) {
							linkPrio += link.priority;
						}
						menu.addEntry({
							onClick: function() {
								switch (link.linkTarget) {
									case 'samewindow':
										window.location = link.web_interface;
										break;
									case 'newwindow':
										window.open(link.web_interface);
										break;
									case 'embedded':
										topic.publish('/portal/iframes/open', link.dn, link.name, link.logo, link.href);
										break;
								}
							},
							label: link.name,
							priority: basePrio + linkPrio
						});
					}
				}
			}
		},

		// TODO
		startup: function() {
			window.p = this;
			this.inherited(arguments);
			this.resize();
		},

		resize: function() {
			// TODO call other times too
			window.requestAnimationFrame(function() {
				for (const titleNode of document.querySelectorAll('.tile__name')) {
					if (titleNode.scrollWidth > titleNode.clientWidth) {
						titleNode.title = titleNode.innerHTML;
					} // TODO else case remove title
				}
			});

			this._resizeIframeTabs();
		},

		_resizeIframeTabs: function() {
			tools.toggleVisibility(this.iframeTabs, true);
			this.set('mobileTabsView', this.iframeTabs.domNode.scrollWidth > this.iframeTabs.domNode.clientWidth);
		},

		_applyAttributes: function() {
			this.inherited(arguments);
			const prefix = '_compute';
			for (const name in this.constructor.prototype) {
				if (name.startsWith(prefix)) {
					const attrName = name.substring(prefix.length);
					this.set(attrName, this[name]());
				}
			}
			for (const name in this.constructor.prototype) {
				if (name.startsWith('_bind')) {
					this[name]();
				}
			}
		}
	});
});

